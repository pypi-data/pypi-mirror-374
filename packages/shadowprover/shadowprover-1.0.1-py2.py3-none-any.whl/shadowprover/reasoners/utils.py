from syntax.expression import is_atomic
from shadowprover.syntax.expression import make_and, make_if, make_or, make_universal, r
from syntax.expression import Expression, is_atomic
from edn_format import Symbol

def get_ground_instances(predicate:Symbol, state):
    return set(filter(lambda x: is_atomic(x) and x.head == predicate ,state))

def complete(formulae):
    arity = len(list(formulae)[0].args)
    predicate = list(formulae)[0].head
    variables = [r(f"?x{i}") for i in range(1, arity +1)]
    arg_combinations = map(lambda f: f.args, formulae)
    consequent = make_or([ make_and([r(f"(= {var} {arg})")  for var, arg in zip(variables, arg_combination)])  for arg_combination in arg_combinations ])
    antecedent = Expression(predicate, variables)
    kernel = make_if(antecedent, consequent)
    return make_universal(variables, kernel)
