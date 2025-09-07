import sys

 
# append the path of the
# parent directory
sys.path.append("..")
sys.path.append("../py_laser")

sys.path.append("../py_laser")


from edn_format import loads_all, Keyword
from syntax.reader import r, read_symbol_or_symbols
from syntax.expression import *
from reasoners.fol_prover import fol_prove as fol_prove
from syntax.reader import read_all_problems

def print_success_message(message):
    print(f"\033[32m \u2713 \033[0m {message}")

def print_fail_message(message):
    print(f"\033[32m \u274c \033[0m {message}")

def tests_runner(prover, file_path, banner="", is_completness=True):
    problems = read_all_problems(file_path)
    print("="*5, banner, "="*5)

    
    for i, problem in enumerate(problems):
        proof_found, proof = prover(problem.assumptions.values(), problem.goal)
        problem_name = problem.name or f"unamed problem - {i}"
        if proof_found:
            if is_completness:
                print_success_message(problem_name)
            else:
                print_fail_message(problem_name)

        else:
            if not is_completness:
                print_success_message(problem_name)
            else:
                print_fail_message(problem_name)


tests_runner(fol_prove, "specs/fol_completeness.clj", "FOL Completeness", True)
tests_runner(fol_prove, "specs/fol_soundness.clj", "FOL Soundness", False)