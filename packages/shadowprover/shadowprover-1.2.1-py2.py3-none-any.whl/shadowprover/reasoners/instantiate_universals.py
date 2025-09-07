import itertools

from ..syntax.expression import get_bound_variables
from ..unifiers.first_order_unify import unify

def get_instantiations_of_universal(univeral, base):

    var =  get_bound_variables(univeral)[0]
    universal_subs = set(filter(lambda f: var in f.get_sub_expressions() and f!=var, univeral.get_sub_formulae()))
    instantiated = set()
    kernel = univeral.args[-1]
    for x, y in itertools.product(universal_subs, base):
        theta = unify(x, y)
        if theta and var in theta and theta[var]!=var:
            instantiated.add(kernel.apply_substitution({var: theta[var]}))
    return instantiated