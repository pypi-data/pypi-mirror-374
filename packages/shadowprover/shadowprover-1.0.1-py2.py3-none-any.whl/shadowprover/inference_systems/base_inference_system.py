

from abc import (
  ABC,
  abstractmethod,
)

from typing import Set

from .base_schema import Schema
class InferenceSystem(ABC):
    
    def __init__(self, name):
        self.name = name
        
    @abstractmethod
    def get_all_schema(self)-> Set[Schema]:
        ...
