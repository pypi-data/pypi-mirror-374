import edn_format
from .common import Symbol
from edn_format import Keyword, loads_all
from .expression import *
from typing import List
from dataclasses import dataclass
from .expression import Expression

name_keyword = Keyword("name")
description_keyword = Keyword("description")
assumptions_keyword = Keyword("assumptions")
goal_keyword = Keyword("goal")


def read_symbol_or_symbols(expr, is_top=False):
    if type(expr) == edn_format.edn_lex.Symbol:
        return Expression(Symbol(str(expr)), is_top=is_top)

    head, *rest = expr
    return Expression(
        edn_format.Symbol(str(head)),
        list(map(read_symbol_or_symbols, rest)),
        is_top=is_top,
    )


def r(formula_str):
    return read_symbol_or_symbols(edn_format.loads(formula_str), is_top=True)


@dataclass
class Problem:
    name: str
    description: str
    assumptions: List[Expression]
    goal: Expression


def read_problem(problem_spec):
    name = problem_spec[name_keyword]
    if not name:
        raise Exception(f"Problem without name - {str(problem_spec)}")
    description = problem_spec[description_keyword]

    assumption_spec_map = problem_spec[assumptions_keyword]
    assumptions = {
        assumption_name: read_symbol_or_symbols(assumption, is_top=True)
        for assumption_name, assumption in assumption_spec_map.items()
    }

    goal = read_symbol_or_symbols(problem_spec[goal_keyword], is_top=True)

    return Problem(
        name=name, description=description, assumptions=assumptions, goal=goal
    )

def read_all_problems(problems_file: str)->List[Problem]:
    with open(problems_file, "r") as file:
        specs = loads_all(file.read())
    
    return [read_problem(spec) for spec in specs]