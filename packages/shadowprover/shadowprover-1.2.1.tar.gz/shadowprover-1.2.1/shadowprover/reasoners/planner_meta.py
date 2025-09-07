from ..syntax.reader import r
from ..syntax.expression import *
from ..fol.fol_prover import *
from ..syntax.reader import *

from .shadow_prover import *
from ..unifiers.first_order_unify import *
from ..syntax.expression import *

name_keyword = Keyword("name")
description_keyword = Keyword("description")
assumptions_keyword = Keyword("assumptions")
goal_keyword = Keyword("goal")
schema_keyword = Keyword("schema")
name_keyword = Keyword("name")

inputs_keyword = Keyword("inputs")
output_keyword = Keyword("output")



def encode_plan(plan):
    
    if not plan:
        return set()
    else:
        
        return first(plan) | previous(plan)
    

def previous(plan:List[Expression])->Expression:
    return {r(f"(previous {plan[-1].head})")}

def first(plan: List[Expression]):
    return {r(f"(first {plan[0].head})")}