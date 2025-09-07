import sys
import pandas as pd


 
# append the path of the
# parent directory
sys.path.append("..")
sys.path.append("../py_laser")



from edn_format import loads_all, Keyword
from syntax.reader import r, read_symbol_or_symbols
from syntax.expression import *
from reasoners.shadow_prover import shadow_prover 
from syntax.reader import read_all_problems
from inference_systems.reader import read_inference_system
import timeit

def print_success_message(message, total_time):
    print(f"\033[32m \u2713 \033[0m {message} [{total_time} ms]")

def print_fail_message(message, total_time):
    print(f"\033[32m \u274c \033[0m {message} [{total_time} ms]")

logic = read_inference_system(loads("""
{
    :name "DCEC"
    :description "DCEC" 
    
    :schema {

        :R4 {
            :name "R4"
            :inputs [(Knows! ?a ?t ?P)]
            :output [?P]
        }
        :R_K_B {
            :name "Knowledge to belief"
            :inputs [(Knows! ?a ?t ?P)]
            :output (Believes! ?a ?t ?P)
        }
        :Common_to_K1 {
            :name "Common to Knowledge 1"
            :inputs [(Common! ?t ?P)]
            :output (Knows! ?a ?t ?P)

        }

        :Perception_to_Knowledge {
            :name "Common to Knowledge "
            :inputs [(Perceives! ?a ?t ?P)]
            :output (Knows! ?a ?t ?P)

        }    
        
        :Common_to_K2 {
            :name "Common to Knowledge 2 "
            :inputs [(Common! ?t1 ?P)]
            :output (Knows! ?a1 ?t2 (Knows! ?a2 ?t1 ?P))

        }
    }
}
"""))


def tests_runner(prover, file_path, banner="", is_completness=True):
    problems = read_all_problems(file_path)
    print("="*5, banner, "="*5)
    rows = []
    
    for i, problem in enumerate(problems):
        #if problem.name != '*cognitive-calculus-completeness-test-13*':
         #   continue
        start = timeit.default_timer()
        proof_found, proof, answer = prover(logic, problem.assumptions.values(), problem.goal, find_answer=False)
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
    tests_runner(shadow_prover, "specs/cc_completeness.clj", "CC Completeness", True)
    tests_runner(shadow_prover, "specs/cc_soundness.clj", "CC Soundness", False)

end  = timeit.default_timer()

print(f"Total time: {end -start } ")