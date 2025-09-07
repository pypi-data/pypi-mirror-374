from fuzzywuzzy import fuzz
from loguru import logger
from reasoners.fol_prover import fol_prove as fol_prove
from reasoners.shadow_repr import shadow
from syntax.expression import Expression, negated
from syntax.reader import r
from inference_systems.base_inference_system import InferenceSystem
from inference_systems.base_schema import Schema
from unifiers.first_order_unify import unify
from shadowprover.fol.proof import BaseProof, CompoundProof

from typing import Set
from functools import cache


def shadow_prover(
    logic: InferenceSystem,
    inputs: Set[Expression],
    output,
    current_goals=set(),
    verbose=False,
):
    prover_cache = {}
    forwards_cache = {}
    context_prove_cache = {}
    return shadow_prover_internal(
        logic,
        inputs,
        output,
        prover_cache,
        forwards_cache,
        context_prove_cache,
        current_goals,
        verbose,
    )


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
    label=""
):
    base = set(inputs)
    
    proof_found, proof = fol_prove(
            [shadow(b) for b in base], shadow(output), verbose
    )
    if proof_found:
        return proof_found, proof
    
    position = (frozenset(base), output)
    if position in context_prove_cache:
            proof_found, proof = context_prove_cache[position]
    else:
        proof_found, proof = context_prove(
            logic,
            frozenset(base),
            output,
            prover_cache,
            forwards_cache,
            context_prove_cache,
            frozenset(current_goals),
            verbose,
            depth,
        )
        context_prove_cache[position] = proof_found, proof
    if proof_found:
        return proof_found, proof

    while not proof_found:
        delta = forwards(logic, base, output, verbose)
        base = base.union(delta)
        added_size = len(delta)
        proof_found, proof = fol_prove(
                [shadow(b) for b in base], shadow(output), verbose
        )
        if proof_found:
            return proof_found, proof
        position = (frozenset(base), output)
        
        if position in context_prove_cache:
                proof_found, proof = context_prove_cache[position]
        else:
            proof_found, proof = context_prove(
                logic,
                frozenset(base),
                output,
                prover_cache,
                forwards_cache,
                context_prove_cache,
                frozenset(current_goals),
                verbose,
                depth,
            )
            context_prove_cache[position] = proof_found, proof
            
        if proof_found:
            return proof_found, proof
        if added_size == 0:
            break

    return False, None


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
    return all_derived


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
):
    modal_type = output.modal_type
    agent = output.agent
    time = output.time

    if not modal_type or not inputs:
        return False, None

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

    position = (frozenset(context_inputs), context_output)
    if position in prover_cache:
        return prover_cache[position]
    else:
        proof_found, proof = shadow_prover_internal(
            logic,
            context_inputs,
            context_output,
            prover_cache,
            forwards_cache,
            context_prove_cache,
            current_goals.union(set([context_output])),
            verbose=verbose,
            depth=depth + 1,
        )
        prover_cache[position] = proof_found, proof

    if not proof_found:
        return proof_found, proof
    else:
        return proof_found, CompoundProof(
            f"context_proof {[inputs, modal_type, agent, time]}", [proof]
        )


def contributing_or_matching_context(expression, modal_type, agent, time) -> bool:
    return (
        expression.modal_type == modal_type
        and expression.agent == agent
        and time
        and expression.time
        and expression.time <= time  # TODO: pluggable with context?
    )
def temp(conditional, base, hypothetical):
   if conditional not in base and hypothetical not in base and False:
                        position = (frozenset(base.union(set([hypothetical]))), output)
                        if position in prover_cache:
                            proof_found, proof = prover_cache[position]
                        else:
                            proof_found, proof = shadow_prover_internal(
                                        logic,
                                        base.union(set([hypothetical])),
                                        output,
                                        prover_cache,
                                        forwards_cache,
                                        context_prove_cache,
                                        current_goals.union(set([output])),
                                        verbose=verbose,
                                        depth=depth + 1,
                                        label=f"hypothetical-cond [{hypothetical}]"
                            )
                            prover_cache[position] = proof_found, proof
                            
                        if proof_found:
                            base.add(conditional)
                            #break
                