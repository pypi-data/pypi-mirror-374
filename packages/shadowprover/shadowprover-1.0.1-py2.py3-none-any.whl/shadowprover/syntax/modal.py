from typing import List
from pydantic import BaseModel
from .common import *


class ModalExpression(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    modal_type: str
    expression_head : List[str]
    min_args : int = 0
    max_args : int = 10
    has_agent : bool = True
    
def get_modal_expression_type(head: Symbol)->str:
    """_summary_

    Args:
        head (Symbol): _description_

    Returns:
        str: _description_
    """
    for modal_expresison_def in modal_expresson_defs:
        if str(head) in modal_expresison_def.expression_head:
            return modal_expresison_def
    
    
modal_expresson_defs = [
    ModalExpression(modal_type="belief",
                    expression_head=[
                        "Believes!", "Believed!", "Believing!", "Believes",
                        "Believed", "Believing"
                    ],
                    min_args=2,
                    max_args=3),
    ModalExpression(modal_type="knowledge",
                    expression_head=[
                        "Knows!",
                        "Knew!",
                    ],
                    min_args=2,
                    max_args=3),
    ModalExpression(modal_type="perception",
                    expression_head=["Sees!", "Perceives!", "Saw!"],
                    min_args=2,
                    max_args=3),
    ModalExpression(
        modal_type="common-knowledge",
        expression_head=["Common!", "CommonlyKnown!", "CommonKnowledge!"],
        min_args=1,
        max_args=2,
        
        has_agent=False),
    ModalExpression(
        modal_type="attention",
        expression_head=["Attention!","AttendTo!", "Focus!"],
        min_args=1,
        max_args=2,
        has_agent=False),
    
    ModalExpression(
        modal_type="attention-obj",
        expression_head=["AttentionObj!", "AttendToObj!", "FocusObj!"],
        min_args=1,
        max_args=2,
        has_agent=False)
]

