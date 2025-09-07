

from abc import ABC
from typing import List

class Proof(ABC):
    
    pass


class BaseProof(Proof):
    
    def __init__(self, name:str, justification:str):
        self.name = name
        self.justification = justification
        
    def __repr__(self):
        return f"[BaseProof {self.name} {self.justification}]"
        
class CompoundProof(Proof):
    
    def __init__(self, name:str, sub_proofs:List[Proof]):
        self.name = name
        self.sub_proofs = sub_proofs
        
    def __repr__(self):
        return f"[CompoundProof {self.name} {self.sub_proofs}]"
        