from .eprover import run_eprover_with_string_input
from .tptp import make_annotated_tptp_formula, to_tptp_formula
from .proof import BaseProof, CompoundProof
import edn_format
from pyparsing import SkipTo, Word, alphas, Literal, Suppress, Group, delimitedList, alphanums

from ..syntax.expression import get_bound_variables
from ..syntax.reader import r
# Define the grammar
SZS = Literal("SZS")
answers = Literal("answers")
Tuple = Literal("Tuple")
open_bracket = Literal("[")
close_bracket = Literal("]")
rest = Literal("|_")
term = Word(alphanums)  # terms are words consisting of alphabetic characters
terms = Group(delimitedList(term))  # list of comma-separated terms

# Full parser for the expected output format
parser = SkipTo(SZS)+ SZS + answers + Tuple + open_bracket + open_bracket + terms + close_bracket + rest + close_bracket 
import itertools

def parse_answers(result_from_prover):


   # Example EProver output
   #"SZS answers Tuple [[plato, greece]|_]\n"

    # Parse the output
    parsed_output = parser.parseString(result_from_prover)
    # Extract terms
    extracted_terms = parsed_output[6]  # The terms are in the 4th position (0-indexed)

    # Optionally, convert to EDN format (using edn_format)
    edn_data = edn_format.dumps(extracted_terms.asList())
    parsed_edn = edn_format.loads(edn_data)
    return parsed_edn
##hacky
def mutiple_answers_fol_prove(inputs, output, max_answers=5): 
    seen = set()
    final_answers = []
    count = 0
    for perm in itertools.permutations(inputs):
        (found, proof, answers) = fol_prove(perm, output, find_answer=True, verbose=False)
        if not found:
            return (False, proof, None) 
        else:
            if answers:
                count = count + 1
                if str(answers[0]) not in seen:
                    
                    final_answers +=[answers[0] ]
                    seen.add(str(answers[0]))
                if count >= max_answers:
                    break
            else:
                break
            

        
    return (True, ".." , final_answers)

    
def fol_prove(inputs, output, find_answer=False, verbose=False, max_answers=5):
    tptp_inputs = [
        make_annotated_tptp_formula("fof", f"input_{i}", "axiom", to_tptp_formula(inp))
        for (i, inp) in enumerate(inputs)
    ]
    tptp_output = make_annotated_tptp_formula(
        "fof", "output", "question", to_tptp_formula(output)
    )
    input_spec = "\n".join(tptp_inputs) + "\n" + tptp_output
    completed_process = run_eprover_with_string_input(input_spec,find_answer, max_answers)

    if verbose:
        print(input_spec)

    stdout = str(completed_process.stdout)

    # if completed_process.returncode==3:
    #     print(input_spec)
    #     print(completed_process.stderr)
    if completed_process.returncode != 0:
        return False, completed_process.stderr, None

    if find_answer:
        if "# Proof found!" in stdout:
            answers = list(filter(lambda x: "SZS answers Tuple" in x, stdout.split("\\n#")))
            variables = get_bound_variables(output)
            return True, BaseProof("eprover", stdout), list(map(lambda ans: dict(zip(variables, map(r, parse_answers(ans)))), answers))
        else:
            False, [], None
    else:
        return "# Proof found!" in stdout,  BaseProof("eprover", stdout), None #completed_process.stdout
