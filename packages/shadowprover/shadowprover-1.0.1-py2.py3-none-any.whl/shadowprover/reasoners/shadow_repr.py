

import re

from ..syntax.expression import *
from ..syntax.reader import r
from ..unifiers.first_order_unify import unify


def shadowable_str_repr(formula):
    formula_str = str(formula)
    replacement_map = {
        r"[(]": "_l_",
        r"[)]": "_r_",
        r"[[]]": "_l_",
        r"[]]": "_r_",
        r"\s": "__"
    }
    for key, value in replacement_map.items():
        formula_str = re.sub(key, value, formula_str)
    return formula_str

##
FORMULA_MAP = {
    
}
COUNTER = 0
def shadow(formula:Expression)->Expression:
    if  is_equals(formula) or is_atomic(formula):
        return formula#r("Shadow_" + shadowable_str_repr(formula))
    #is_exists(formula) or is_forall(formula) or is_equals(formula) or
    
    shadowed_args = [str(shadow(arg)) for arg in formula.args or []]
      
    
    if is_not(formula):
        return r(f"(not {shadowed_args[0]})")
    
    if is_if(formula):
        return r(f"(if {shadowed_args[0]} {shadowed_args[1]})")
    
    if is_iff(formula):
        return r(f"(iff {shadowed_args[0]} {shadowed_args[1]})")
    
    if is_and(formula):
        return r(f"(and {' '.join(shadowed_args)})")

    if is_or(formula):
        return r(f"(or {' '.join(shadowed_args)})")
    
    if is_forall(formula):
        vars = formula.args[0]
        return r(f"(forall {formula.args[0]} {' '.join(shadowed_args[1:])})")
    if is_exists(formula):
        vars = formula.args[0]
        return r(f"(exists {formula.args[0]}  {' '.join(shadowed_args[1:])})")

    if is_modal(formula):
        global FORMULA_MAP, COUNTER

        if formula in FORMULA_MAP:
            return FORMULA_MAP[formula]

        # for f, s in FORMULA_MAP.items():
        #     if unify(formula, f):
        #        return s
        
        FORMULA_MAP[formula] = r(f"Shadowed_{COUNTER}")
        COUNTER = COUNTER + 1

    
        return FORMULA_MAP[formula] 

    return r("Shadow_" + shadowable_str_repr(formula))

  
def fol_reify(formula:Expression, level=0)->Expression:
    annotation = 'inner' if level > 0 else ''
    
    if  is_equals(formula) or is_atomic(formula) :
            if not is_equals(formula):
                args = formula.args or []
                return r(f"(holds{annotation}{len(args)} {str(formula.head)} {' '.join(map(str, args))} )")
            else:
                args = formula.args or []

                return r(f"(holds{annotation}{len(args)} eqv {args[0]} {args[1]})")
        
    #is_exists(formula) or is_forall(formula) or is_equals(formula) or
    
    fol_reified_args = [str(fol_reify(arg)) for arg in formula.args or []]
      
    
    if is_not(formula):
        return r(f"(not {fol_reified_args[0]})")
    
    if is_if(formula):
        return r(f"(if {fol_reified_args[0]} {fol_reified_args[1]})")
    
    if is_iff(formula):
        return r(f"(iff {fol_reified_args[0]} {fol_reified_args[1]})")
    
    if is_and(formula):
        return r(f"(and {' '.join(fol_reified_args)})")

    if is_or(formula):
        return r(f"(or {' '.join(fol_reified_args)})")
    
    if is_forall(formula):
        vars = formula.args[0]
        return r(f"(forall {formula.args[0]} {' '.join(fol_reified_args[1:])})")
    if is_exists(formula):
        vars = formula.args[0]
        return r(f"(exists {formula.args[0]}  {' '.join(fol_reified_args[1:])})")

    if is_modal(formula):

        fol_reified_args = [str(fol_reify(arg, level+1)) for arg in formula.args or []]
        return r(f"(holds{annotation}{len(fol_reified_args)} {str(formula.head).lower().replace('!', '')}  {' '.join(map(str, fol_reified_args))} )")

    return r("Shadow_" + shadowable_str_repr(formula))

  