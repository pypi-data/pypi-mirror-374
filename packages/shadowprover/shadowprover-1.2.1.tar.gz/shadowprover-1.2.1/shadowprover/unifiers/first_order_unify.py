from typing import Optional, Dict
from ..syntax.expression import Expression


def unify(
    x: Expression, y: Expression, theta=None
) -> Optional[Dict[Expression, Expression]]:
    
    theta = theta or {}

    if x == y:
        return {}

    if x.is_variable() and x not in y.get_sub_expressions() and theta.get(x, y) == y:
        return {x: y}

    if y.is_variable() and y not in x.get_sub_expressions() and theta.get(y, x) == x:
        return {y: x}

    # not equal and both not variables
    if x.is_atomic() or y.is_atomic():
        # not equal, can't unify atomic
        return None

    if x.head != y.head:
        return None

    args_x = x.args
    args_y = y.args

    if len(args_x) != len(args_y):
        return None

    for arg_x, arg_y in zip(args_x, args_y):
        theta_arg = unify(arg_x, arg_y, theta)
        if theta_arg is None:
            return None
        else:
            theta.update(theta_arg)

    return theta
