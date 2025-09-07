
from functools import cache
from ..syntax.reader import r
from ..syntax.expression import *
from ..fol.fol_prover import fol_prove
from ..syntax.reader import *

from ..unifiers.first_order_unify import *
from ..syntax.common import Symbol
from ..syntax.expression import *
from ..syntax.expression import Expression
from ..syntax.common import Symbol
from ..syntax.expression import *
from ..syntax.expression import Expression

 
 

class SST_Prover():
    def __init__(self, e_prover_invocation="./eprover"):
        self.e_prover_invocation = e_prover_invocation
        self.PERCEPTION = r('perception')
        
    def __translates__(self, formula_str):
        return self.__translate__(r(formula_str))
    
    def __translate__(self, formula: Expression, enclosing_context=lambda x: r(f"(context top all all {x})"), is_object=False):
        if formula.is_modal():
            kernel = formula.get_kernel()
            cfun = lambda y: enclosing_context(r(f"(context {formula.get_modal_type()} {str(formula.agent) or 'all'} {formula.get_time()} {y})"))
            return self.__translate__(kernel, cfun) 
        elif formula.is_predicate():
            end_context = str(enclosing_context("end"))
            if is_equals(formula):
                x = formula.args[0]
                y = formula.args[1]
                return r(f"(= {str(self.__translate__(x, enclosing_context, is_object=True))} {str(self.__translate__(y, enclosing_context, is_object=True),)})")
            else:
                if formula.args is None:
                    if is_object:
                        return Expression(Symbol("object"), [r(str(formula.head)),r(end_context)]) 
                    else:
                        return Expression(Symbol("prop"), [r(str(formula.head)),r(end_context)]) 
                
                else:
                    # return Expression(formula.head, list(map(lambda x: self.__translate__(x, enclosing_context, is_object=True), formula.args)) + [r(end_context)])                     

                    if is_object:
                        return Expression(Symbol(f"object{len(formula.args)}"), [r(str(formula.head))] +list(map(lambda x: self.__translate__(x, enclosing_context, is_object=True), formula.args)) + [r(end_context)]) 
                    else:    
                        return Expression(Symbol(f"proposition{len(formula.args)}"), [r(str(formula.head))] +list(map(lambda x: self.__translate__(x, enclosing_context, is_object=True), formula.args)) + [r(end_context)]) 
        
        elif is_quantifier(formula):
            operator = formula.head
            args = formula.args
            vars = str(args[0])
            rest_args = " ".join(list(map(str, map(lambda x: self.__translate__(x, enclosing_context), formula.args[1:]))))
            
            return r(f"({operator} {vars} {rest_args})") 

        else:
            operator = formula.head
                    
            args = " ".join(list(map(str, map(lambda x: self.__translate__(x, enclosing_context), formula.args))))
            
            return r(f"({operator} {args})") 
        


    def apply_modal_inferences(self, formula):
        inferences = set()
            # apply perception -> belief
        if self.PERCEPTION in formula.sub_expressions:
            consequent = formula.apply_substitution({r("perception"): r("belief")})

            if consequent!=formula:
                inferences = inferences | {make_if(formula, consequent)}
            
        return inferences

    def sst_prove(self, givens, goal, find_answer=False, max_answers=5):
        inference_schemata = list(map(r, [
            
        """(forall [?a ?t ?P] 
             (if
                (prop ?P (context top all all (context knowledge ?a ?t end)))
                (prop ?P (context top all all (context belief ?a ?t end)))
            )
        )
        """, # ax_K_B =
            """(forall [?P ?a ?t] (if (proposition1 ?P (context top all all (context knowledge ?a ?t end))) 
                                      (proposition1 ?P (context top all all end))))""",
            """(forall [?P ?a ?t] (if (prop ?P (context top all all (context belief ?a ?t end))) 
                                      (prop ?P (context top all all end))))""",                                      
            """(forall [?P ?arg1 ?a ?t] (if (prop ?P ?arg1 (context top all all (context knowledge ?a ?t end))) 
                                      (prop ?P ?arg1 (context top all all end))))"""                                      
        ]))
    
        
        inputs_t = set(map( self.__translate__, givens)) 
        inference_schemata = set()
        for input_t in inputs_t:
            inference_schemata = inference_schemata | self.apply_modal_inferences(input_t)
        goal_t = self.__translate__(goal)
        return fol_prove(inputs_t | inference_schemata, goal_t, find_answer=find_answer, max_answers=max_answers)    

    def prove(self, givens, goal, find_answer=False, max_answers=5):
        result = self.sst_prove(list(map(r, givens)), r(goal), find_answer, max_answers )
        
        return {
            "proof_found": result[0],
            "answers": result[2]
        }

    def prove2(self, givens, goal, find_answer=False, max_answers=5):
        return self.sst_prove(givens,goal, find_answer, max_answers )
        
        # return {
        #     "proof_found": result[0],
        #     "proof": result[1]
        #     "answers": result[2]
            
        # }

    def get_cached_shadow_prover(self, find_answer=True, max_answers=5):
        @cache
        def cached_t_prover(inputs, output, find_answer=find_answer, max_answers=max_answers):
            return self.prove(inputs, output, find_answer=find_answer, max_answers=max_answers)
        
        def _prover_(inputs, output, find_answer=find_answer, max_answers=max_answers):
            return cached_t_prover(frozenset(inputs), output, find_answer, max_answers=max_answers)
        
        return _prover_

    def get_cached_shadow_prover2(self, find_answer=True, max_answers=5):
        @cache
        def cached_t_prover(inputs, output, find_answer=find_answer, max_answers=max_answers):
            return self.prove2(inputs, output, find_answer=find_answer, max_answers=max_answers)
        
        def _prover_(inputs, output, find_answer=find_answer, max_answers=max_answers):
            return cached_t_prover(frozenset(inputs), output, find_answer, max_answers=max_answers)
        
        return _prover_
