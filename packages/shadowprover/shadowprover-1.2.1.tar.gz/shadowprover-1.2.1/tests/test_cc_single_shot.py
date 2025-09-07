import sys
import pandas as pd


 
# append the path of the
# parent directory
sys.path.append("..")
sys.path.append("../src/shadowprover")



from edn_format import loads_all, Keyword
from syntax.reader import r, read_symbol_or_symbols
from syntax.expression import *
from reasoners.single_shot_shadow_prover import tprove 
from syntax.reader import read_all_problems
from inference_systems.reader import read_inference_system
import timeit

def print_success_message(message, total_time):
    print(f"\033[32m \u2713 \033[0m {message} [{total_time} ms]")

def print_fail_message(message, total_time):
    print(f"\033[32m \u274c \033[0m {message} [{total_time} ms]")



def tests_runner(prover, file_path, banner="", is_completness=True):
    problems = read_all_problems(file_path)
    print("="*5, banner, "="*5)
    rows = []
    
    for i, problem in enumerate(problems):
        #if problem.name != '*cognitive-calculus-completeness-test-13*':
         #   continue
        start = timeit.default_timer()
        proof_found, proof, answer = prover(problem.assumptions.values(), problem.goal, find_answer=False)
        end = timeit.default_timer()
        total_time = round(1000* (end - start))
        problem_name = problem.name or f"unamed problem - {i}"
        rows.append({"problem": problem.name, "time": end -start})
        print(total_time)
        if proof_found:
            if is_completness:
                print_success_message(problem_name, total_time)
            else:
                print_fail_message(problem_name, total_time)

        else:
            if not is_completness:
                print_success_message(problem_name, total_time)
            else:
                print_fail_message(problem_name, total_time)
    df = pd.DataFrame(rows)
    df.to_csv("timing_object_level_attention", index=False,  mode='a',header=False)

start = timeit.default_timer()

for i in range(1):
    print(i)
    tests_runner(tprove, "specs/cc_completeness_single_shot.clj", "CC Completeness", True)
    tests_runner(tprove, "specs/cc_soundness.clj", "CC Soundness", False)

end  = timeit.default_timer()

print(f"Total time: {end -start } ")