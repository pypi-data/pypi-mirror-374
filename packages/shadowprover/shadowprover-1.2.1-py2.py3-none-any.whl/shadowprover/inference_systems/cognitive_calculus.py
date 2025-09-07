
from edn_format import loads

from ..reasoners import shadow_prover

from .reader import read_inference_system
from .base_inference_system import InferenceSystem
from ..syntax.expression import Expression
from ..reasoners.shadow_prover import shadow_prover as sprover

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
        :Common_to_K2 {
            :name "Common to Knowledge 2 "
            :inputs [(Common! ?t ?P)]
            :output (Knows! ?a t (Knows! ?a ?t ?P))

        }
        :Perception_to_Knowledge {
            :name "Common to Knowledge "
            :inputs [(Perceives! ?a ?t ?P)]
            :output (Knows! ?a ?t ?P)

        }    
    }
}

"""))


def cc_prover(state, test, find_answer=True, max_answers=5):
    return sprover(logic, state, test, find_answer=find_answer, max_answers=max_answers)