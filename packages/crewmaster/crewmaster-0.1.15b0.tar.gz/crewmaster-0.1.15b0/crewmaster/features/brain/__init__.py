"""
Handle the connection with the LLM model.

"""

from .brain_base import BrainBase
from .brain_types import (
    BrainInput,
    BrainOutput,
    SituationBuilderFn,
    InstructionsTransformerFn,
)



__all__ = [
    "BrainBase",
    "BrainInput",
    "BrainOutput",
    "SituationBuilderFn",
    "InstructionsTransformerFn",
]
