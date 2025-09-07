import subprocess
from functools import cache
import os
EPROVER_HOME = os.environ['EPROVER_HOME']
e_prover_invocation = os.path.join(EPROVER_HOME, "PROVER/eprover-ho")
# @cache
# def run_eprover_with_string_input(input_spec: str, find_answer=False, max_answers=5) -> str:
#    if find_answer:
#       options = ["/Users/naveensundar/projects/py_laser/eprover/PROVER/eprover-ho",  "--auto", f"--answers={max_answers}"] 
#    else:
#       options = ["/Users/naveensundar/projects/py_laser/eprover/PROVER/eprover-ho", "--auto"] 
#    completed_process = subprocess.run(
#        options, input=input_spec.encode(), capture_output=True
#     )
#    return completed_process

#"/Users/naveensundar/projects/py_laser/eprover/PROVER/eprover-ho
@cache
def run_eprover_with_string_input(input_spec: str, find_answer=False, max_answers=5) -> str:
   
   if find_answer:
      options = [e_prover_invocation,  "--auto", f"--answers={max_answers}", "--soft-cpu-limit=1"] 
   else:
      options = [e_prover_invocation, "--auto"] 
   try:
      completed_process = subprocess.run(
         options, input=input_spec.encode(), capture_output=True,timeout=0.1
      )
      return completed_process
   except subprocess.TimeoutExpired:
      return subprocess.CompletedProcess(args=options, returncode=-1, stdout="")
