from ..syntax.expression import *
from ..syntax.reader import r


def to_tptp_formula(expression, is_var=False, var_set=set()):
    args = expression.args

    if not args:
        if is_var or str(expression).startswith("?") or str(expression).endswith("?") or expression in var_set:
            return str(expression).replace("?", "_").upper()
        else:
            return str(expression).lower()

    args_in_tptp = list(map(lambda x:to_tptp_formula(x, var_set=var_set), args))

    if is_equals(expression):
        return f"({args_in_tptp[0]} = {args_in_tptp[1]})"

    if is_not(expression):
        return f"~ ({args_in_tptp[0]})"

    if is_and(expression):
        return f"({' & '.join(args_in_tptp)})"

    if is_or(expression):
        return f"({' | '.join(args_in_tptp)})"

    if is_if(expression):
        return f"({args_in_tptp[0]} => {args_in_tptp[1]})"

    if is_iff(expression):
        return f"({args_in_tptp[0]} <=> {args_in_tptp[1]})"

    if is_quantifier(expression):
        variables_map = {
            variable: r(str(variable).replace("?", "_").upper())
            for variable in get_bound_variables(expression)
        }
        new_variable_names = list(map(str, variables_map.values()))
        kernel = args[1].apply_substitution(variables_map)
        kernel_in_tptp = to_tptp_formula(kernel, is_var=False, var_set=var_set.union(set(variables_map.values())))
        if is_forall(expression):
            return f"(! [{', '.join(new_variable_names)}]: ({kernel_in_tptp}))"

        if is_exists(expression):
            return f"(? [{', '.join(new_variable_names)}]: ({kernel_in_tptp}))"

    return f"{str(expression.head).lower()}({', '.join(args_in_tptp)})"


def make_annotated_tptp_formula(
    language, name, role, formula, source="none", useful_info="none"
):
    return f"{language}({name}, {role}, {formula})."  # , {source}, {useful_info})."
