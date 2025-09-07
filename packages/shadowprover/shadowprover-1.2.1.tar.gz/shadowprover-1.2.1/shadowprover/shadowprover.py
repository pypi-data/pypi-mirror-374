"""Main module."""
from .reasoners.fol_prover import fol_prove
from .syntax.expression import *
from .syntax.reader import r 
from edn_format import loads_all


print(fol_prove([r("(if P Q)"), r("P")], r("Q"), True)[0])


import edn_format
from syntax.common import Symbol

from syntax.expression import Expression


def read_symbol_or_symbols(expr, is_top=False):
    if type(expr) == edn_format.edn_lex.Symbol:
        return Expression(Symbol(str(expr)), is_top=is_top)
    
    head, *rest = expr
    return Expression(edn_format.Symbol(str(head)), list(map(read_symbol_or_symbols, rest)), is_top=is_top)
        
def r(formula_str):
    return read_symbol_or_symbols(edn_format.loads(formula_str), is_top=True)

