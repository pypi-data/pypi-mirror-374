import sys
# append the path of the
# parent directory
sys.path.append(".")
sys.path.append("./syntax")
sys.path.append("./reasonsers")

from edn_format import loads_all, Keyword
from syntax.reader import r, read_symbol_or_symbols
from syntax.expression import *
from reasoners.fol_prover import *
from syntax.reader import *
from reasoners.shadow_prover import *
from unifiers.first_order_unify import *
import edn_format
from syntax.common import Symbol
from edn_format import Keyword, loads_all
from syntax.expression import *
from typing import List
from dataclasses import dataclass
from syntax.expression import Expression
import edn_format
from syntax.common import Symbol
from edn_format import Keyword, loads_all
from syntax.expression import *
from typing import List
from dataclasses import dataclass
from syntax.expression import Expression
from inference_systems.reader import read_inference_system

name_keyword = Keyword("name")
description_keyword = Keyword("description")
assumptions_keyword = Keyword("assumptions")
goal_keyword = Keyword("goal")
schema_keyword = Keyword("schema")
name_keyword = Keyword("name")

inputs_keyword = Keyword("inputs")
output_keyword = Keyword("output")

problem = read_problem(loads_all("""
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

{:name        "*cognitive-calculus-completeness-test-26*"
 :description "universal intro inside a knows"
 :assumptions {
                1 (Perceives! jones now (not (effective Switch)))
                2 (Knows! jones now (Option switch-stay stay))
                3 (Knows! jones now (Option switch-stay switch))
                4 (Knows! jones now (forall x (if (Option switch-stay x)
                                                (or (= x switch) (= x stay)))))
                5  (if
                     (and  (Believes! jones now  (not (Effective switch)))
                           (Believes! jones now (Option switch-stay switch)))

                     (Believes! jones now (not (Useful (analysis switch-stay)))))
                6 (if  (Believes! jones now (not (Useful (analysis switch-stay))))

                (Desires! jones now (holds (does jones (refrain (analysis switch-stay))) now)))

                }

 :goal
 (Knows! jones now (not (effective Switch)))
    
 }


""")[0])
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


print(shadow_prover(logic, list(problem.assumptions.values()), problem.goal, find_answer=True, verbose=0))