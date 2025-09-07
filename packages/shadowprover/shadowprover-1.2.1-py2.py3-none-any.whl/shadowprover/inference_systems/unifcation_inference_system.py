

from typing import Set
from .base_schema import Schema
from .base_inference_system import InferenceSystem

class UnificationInferenceSchema(InferenceSystem):
        
    def __init__(self, name, schema):
        self.name = name        
        self.schema = schema 
    
    def get_all_schema(self)-> Set[Schema]:
        return self.schema

    def __repr__(self) -> str:
        divider_1 = "=" * 20
        divider_2 = "-" * 20
        schema_str = f"\n{divider_2}\n\n".join(list(map(repr,self.schema)))
        return f"{divider_1}\n\t{self.name}\n{divider_1}\n{schema_str}\n\n\n{divider_1} "