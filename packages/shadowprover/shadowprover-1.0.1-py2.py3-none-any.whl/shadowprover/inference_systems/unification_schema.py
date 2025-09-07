

from abc import (
  ABC,
  abstractmethod,
)
from ..syntax.expression import Expression
from typing import Set, Optional
import itertools
from ..unifiers.first_order_unify import unify
from .base_schema import Schema
import itertools 
class UnificationSchema(Schema):
        
    def __init__(self, name, inputs, output):
        self.name = name        
        self.inputs = inputs
        self.output = output
        max_input_size = max(map(len, map(str, self.inputs)))
        self.mode = "forward" if len(str(self.output )) < max_input_size  else "reverse"
    
    
    def reverse_apply(self, conclusion: Expression)->Optional[Set[Expression]]:
        if self.mode == 'forward':
            return None
        
        theta = unify(conclusion, self.output) 
        if theta:
            return set([inp.apply_substitution(theta) for inp in self.inputs ])
    
    def forward_apply(self, givens: Set[Expression])->Set[Expression]:
        #if self.mode == 'reverse':
        #    return None

        result = set()
        permutations = itertools.permutations(givens, len(self.inputs))
        for permutation in permutations:
            theta = {}
            for given, inp in zip(permutation, self.inputs):
                theta = unify(given, inp, theta)
                if theta:
                    result.add(self.output.apply_substitution(theta))
        return result
    
    def __repr__(self) -> str:
        inps = str([inp for inp in self.inputs])
        divider = "-"*len(inps)
        tabs_sep = "   "
        return f"""{inps}\n{divider} [{self.name}]\n{tabs_sep}{self.output}"""