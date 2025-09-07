

from abc import (
  ABC,
  abstractmethod,
)
from ..syntax.expression import Expression
from typing import Set, Optional

class Schema(ABC):
        
    @abstractmethod
    def reverse_apply(self, conclusion: Expression)->Optional[Set[Expression]]:
        ...

    @abstractmethod
    def forward_apply(self, givens: Set[Expression])->Set[Expression]:
        ...
