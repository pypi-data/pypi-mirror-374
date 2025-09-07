import itertools
from edn_format import Symbol
from fuzzywuzzy import fuzz
from loguru import logger
from ..fol.fol_prover import mutiple_answers_fol_prove
from ..fol.fol_prover import fol_prove as fol_prove
from .instantiate_universals import get_instantiations_of_universal
from .shadow_repr import fol_reify, shadow
from ..syntax.expression import Expression, is_exists, is_forall, is_if, is_or, negated
from ..syntax.reader import r
from ..inference_systems.base_inference_system import InferenceSystem
from ..inference_systems.base_schema import Schema
from ..unifiers.first_order_unify import unify
from ..fol.proof import BaseProof, CompoundProof
from colorama import Fore, Back, Style
from typing import Set
from functools import cache
import time 
PARAMS = {
    "expand_modals_deductive_cloure":False,
    "max_depth": 1.25
}

def get_cached_fol_prover():

    @cache
    def cached_prover(inputs, output, find_answer=False, verbose=False, max_answers=5):
        return fol_prove(inputs, output, find_answer=find_answer, verbose=verbose, max_answers=max_answers)
    
    def _prover_(inputs, output, find_answer=True, verbose=False, max_answers=5):
        return cached_prover(frozenset(inputs), output, find_answer=find_answer, max_answers=max_answers, verbose=verbose)
    
    return _prover_
def shadow_prover(
    logic: InferenceSystem,
    inputs: Set[Expression],
    output,
    current_goals=set(),
    find_answer=False,
    verbose=False,
    max_answers=5
):
    prover_cache = {}
    forwards_cache = {}
    context_prove_cache = {}
    answers = {}
    
    # start = time.time()

    result =  shadow_prover_internal(
        logic,
        inputs,
        output,
        prover_cache,
        forwards_cache,
        context_prove_cache,
        current_goals,
        verbose,
        find_answer=find_answer,
        answers=answers,
        max_answers=max_answers,
        fol_prove=get_cached_fol_prover()
    )
    
    # end = time.time()
    # #print(f"{end-start} {result[0]} {inputs} => {output} ")
    return result

def shadow_prover_internal(
    logic: InferenceSystem,
    inputs: Set[Expression],
    output,
    prover_cache,
    forwards_cache,
    context_prove_cache,
    current_goals=set(),
    verbose=False,
    depth=0,
    label="",
    find_answer=False,
    max_answers=5,
    answers={},
    fol_prove=None
):
    base = set(inputs)
    while len(base) <= PARAMS["max_depth"]*len(inputs):
        if depth == 0:
            pass

        if verbose:
            logger.log(
                "INFO",
                f"ShadowProver {label} {depth}   on {base} -> {output}",
            )
            #import time; time.sleep(0.5)
            indent = f"Depth: {depth}" + "\t"*depth
            print(f"{indent} Given" + Style.DIM + f"{inputs}" + Style.RESET_ALL + Back.LIGHTBLUE_EX + Fore.WHITE + f" goal: {output}" + Style.RESET_ALL)
            print(Style.RESET_ALL)
        N = len(base)
        
        #####################################################################
        ######## Case 0: no answer finding, and input contains output #######
        #####################################################################
        if output in base and not find_answer:
            return True, BaseProof("trivial", f"{output} in inputs"), None

        #####################################################################
        ######## Case 1: output unifies with input with answering finding ###
        #####################################################################       
        new_answers = subproof_unify_output_with_inputs(base, output)        
        if new_answers and not detect_conflicts(answers, new_answers):
            _, _proof, reified_answers = mutiple_answers_fol_prove(
                    [fol_reify(b) for b in base], fol_reify(output), max_answers=max_answers
                )

            return True, BaseProof(f"{output}", f"{new_answers} in inputs"), reified_answers# {**(answers or {}), **new_answers}
       
        #####################################################################
        ######## Case 3: Shadow to FOL                                    ###
        #####################################################################       
        proof_found, proof, answers = fol_prove(
            [shadow(b) for b in base], shadow(output), find_answer=False, verbose=verbose
        )
        if proof_found:
            if not find_answer:
                return proof_found, proof, answers
            else:
                _, _proof, answers = mutiple_answers_fol_prove(
                    [fol_reify(b) for b in base], fol_reify(output), max_answers=max_answers
                )
                return True, proof, answers

        ### Case 3: Proof search within context of output
        position = frozenset(base), output
        if position in context_prove_cache:
            proof_found, proof, answers = context_prove_cache[position]
        else:
            proof_found, proof, answers = context_prove(
                logic,
                frozenset(base),
                output,
                prover_cache,
                forwards_cache,
                context_prove_cache,
                frozenset(current_goals),
                verbose,
                depth,
                find_answer,
                answers=answers,
                            fol_prove=fol_prove
                
            )
            context_prove_cache[position] = proof_found, proof, answers

        if proof_found:
            return proof_found, proof, answers

        if position in forwards_cache:
            delta = forwards_cache[position]
        else:
            delta = forwards(
                logic,
                base,
                output,
                verbose,
            )
            forwards_cache[position] = delta

        base = base.union(delta)

        hypotheticals = propose_hypotheticals(base, output, depth)
    
        if hypotheticals:
            for hypothetical in hypotheticals:
                if hypothetical and hypothetical not in current_goals:
                    position = (frozenset(base), hypothetical)
                    if verbose:
                        print(f"[Hypothetical]  {indent} Given" + Style.DIM + f"{inputs}" + Style.RESET_ALL + Back.LIGHTBLUE_EX + Fore.WHITE + f" goal: {output}" + Style.RESET_ALL)

                    if position in prover_cache:
                        proof_found, proof, answers = prover_cache[position]
                    else:
                        proof_found, proof, answers = shadow_prover_internal(
                            logic,
                            base,
                            hypothetical,
                            prover_cache,
                            forwards_cache,
                            context_prove_cache,
                            current_goals.union(set([hypothetical])),
                            verbose=verbose,
                            depth=depth + 1,
                            label="backwards",
                            find_answer=find_answer,
                            answers=answers,
                            fol_prove=fol_prove
                        )
                        prover_cache[position] = proof_found, proof, answers

                    if proof_found:
                        base.add(hypothetical)
                 
        if len(base) == N:
            return False, "", None
    return False, "", None

def subproof_unify_output_with_inputs(inputs, output):
    answers = {}
    if is_exists(output):
        output = output.kernel
    for b in inputs:
        theta = unify(b, output)
        if theta and output not in theta:
            if not answers:
                answers = {}
            answers.update(theta)
    return answers


def is_deductive_closure_modal(expression):
    return expression.modal_type in ["common-knowledge", "knowledge", "belief", "perception"]

def forwards(logic: InferenceSystem, inputs, output, verbose):
    schema: Set[Schema] = logic.get_all_schema()
    if verbose:
        logger.log(
            "INFO",
            f"Forwards [givens: {inputs} ||  goal: {output}]",
        )
    inputs = inputs if type(inputs) == set else set(inputs)
    all_derived = set()
    for schemata in schema:
        derived = schemata.forward_apply(inputs)
        if derived and derived not in inputs:
            all_derived = all_derived.union(derived)
 
        conjunctions = list(filter(is_or, inputs))
        implications = list(filter(is_if, inputs))
        universals = list(filter(is_forall, inputs))
        if PARAMS["expand_modals_deductive_cloure"]:
            deductive_closed_modals = list(filter(is_deductive_closure_modal, inputs))
        else:
            deductive_closed_modals = []

        for schemata in schema:
            for c in conjunctions:
                l_derived = schemata.forward_apply(set([c.args[0]])).union(set([c.args[0]]))
                r_derived = schemata.forward_apply(set([c.args[1]])).union(set([c.args[1]]))
                prod = itertools.product(l_derived, r_derived)
                for x, y in prod:
                    f = r(f"(or {x} {y})")
                    all_derived.add(f)
            for imp in implications:
                ant, cons = imp.args
                derived = schemata.forward_apply(set([cons])).union(set([cons]))
                for x in derived:
                    f = r(f"(if {ant} {x})")
                    all_derived.add(f)
            for modal in deductive_closed_modals:
                kernel = modal.get_kernel()
                derived = schemata.forward_apply(set([kernel])).union(set([kernel]))
                for x in derived:
                    ## TODO: Make this cleaner
                    f = Expression(modal.head, modal.args[:-1] + [x])
                    all_derived.add(f)
            for universal in universals:
                instantiations = get_instantiations_of_universal(universal, inputs)
                all_derived = all_derived.union(instantiations)



    return set(map(lambda x: x.convert_to_schema(), all_derived))


def context_prove(
    logic,
    inputs,
    output,
    prover_cache,
    forwards_cache,
    context_prove_cache,
    current_goals,
    verbose=False,
    depth=0,
    find_answer=False,
    answers={},
                            fol_prove=None
    
):
    modal_type = output.modal_type
    agent = output.agent
    time = output.time

    if not modal_type or not inputs:
        return False, None, None

    context_inputs = [
        inp.get_kernel()
        for inp in inputs
        if contributing_or_matching_context(inp, modal_type, agent, time)
    ]
    context_output = output.get_kernel()
    if verbose:
        logger.log(
            "INFO",
            f"Context Recursing [{modal_type}, {agent}, {time}] on {context_inputs} -> {context_output}",
        )
            
        indent = '\t' * depth
        print(Back.LIGHTBLUE_EX + f"{indent} Context prove" + Style.DIM + f"{inputs}"  + Back.GREEN + Fore.WHITE + f" goal: {output}" + Style.RESET_ALL)
        print(Style.RESET_ALL)

    position = (frozenset(context_inputs), context_output)
    if position in prover_cache:
        return prover_cache[position]
    else:
        proof_found, proof, answers = shadow_prover_internal(
            logic,
            context_inputs,
            context_output,
            prover_cache,
            forwards_cache,
            context_prove_cache,
            current_goals.union(set([context_output])),
            verbose=verbose,
            depth=depth + 1,
            find_answer=find_answer,
            answers=answers,
                            fol_prove=fol_prove
            
            
        )
        prover_cache[position] = proof_found, proof, answers

    if not proof_found:
        return proof_found, proof, None
    else:
        return proof_found, CompoundProof(
            f"context_proof {[inputs, modal_type, agent, time]}", [proof]
        ), answers


def contributing_or_matching_context(expression, modal_type, agent, time) -> bool:
    return (
        expression.modal_type == modal_type
        and expression.agent == agent
        and time
        and expression.time
        and expression.time <= time  # TODO: pluggable with context?
    )

def propose_hypotheticals2(inputs, output, depth):
    level_1 = propose_hypotheticals(inputs, output)
    if level_1:
        result = set(level_1)
        for item in level_1:
            level_2 = propose_hypotheticals(inputs, item, depth)
            result = set(result).union(set(level_2))
        return result
    else:
        return set(level_1)
    
def propose_hypotheticals(inputs, output, depth):
    base_sub_expressions = set().union(*[b.get_sub_formulae() for b in inputs])
    hypotheticals = list(
            set(output.get_sub_formulae())
            .union(base_sub_expressions)
            .difference(set([output]))
        )
    hypotheticals.sort(
            key=lambda expr: expr.compute_overlap_fraction(inputs, output), reverse=True
        )    
    filtered_hypotheticals = list(filter(lambda expr: expr.compute_overlap_fraction(inputs, output, depth)>0, hypotheticals))
    if not filtered_hypotheticals:
        filtered_hypotheticals = hypotheticals 
        
    filtered_hypotheticals = list(set(filtered_hypotheticals).difference(inputs))
    
    filtered_hypotheticals.sort(
            key=lambda expr: -expr.compute_overlap_fraction(inputs, output)
    )    

    def consequent_contains_or_equals_output(expr):
        return expr.args[1] == output or  output in expr.args[1].get_sub_formulae()
    antecedents = list(map(lambda implication: implication.args[0], filter(lambda expr: is_if(expr) and consequent_contains_or_equals_output(expr), inputs)))
    
    return set(filtered_hypotheticals[:1] + antecedents)

def detect_conflicts(dict1={}, dict2={}):
    if not dict1 or not dict2:
        return False
    for key in dict1.keys() & dict2.keys():
        if dict1[key] != dict2[key]:
            return True

