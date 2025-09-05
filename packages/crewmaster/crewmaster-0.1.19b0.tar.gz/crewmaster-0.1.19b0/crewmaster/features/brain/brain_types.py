"""
Module defining input and output data structures for CrewMaster's Brain system.

This module contains the Pydantic models, type adapters, and callable type
definitions used for representing and handling structured communication
between Brain components. The models are designed for type-safe serialization,
validation, and discrimination between different message types.
"""


from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Union,
    Annotated,
)
from ...core.pydantic import (
    BaseModel,
    Field,
    TypeAdapter,
)
from langchain_core.runnables import (
    RunnableConfig,
)
import structlog

from ..collaborator import (
    AgentMessage,
    AnyMessage,
    TokenUsage
)
from ..skill import (
    ComputationRequested,
    ComputationResult,
)

log = structlog.get_logger()
"Loger para el módulo"

class BrainInputBase(BaseModel):
    """Base class for all Brain input types.

    Attributes:
        messages (List[AnyMessage]): The list of incoming messages.
        user_name (str): The name of the user associated with the input.
        today (str): The current date as a string, used for context.
    """

    messages: List[AnyMessage]
    user_name: str
    today: str


class BrainInputFresh(BrainInputBase):
    """Represents a fresh Brain input request.

    Attributes:
        type (Literal['brain.input.fresh']): The fixed type discriminator for this input.
    """

    type: Literal['brain.input.fresh'] = 'brain.input.fresh'


class BrainInputResults(BrainInputBase):
    """Represents Brain input containing computation results.

    Attributes:
        type (Literal['brain.input.clarification']): The fixed type discriminator for this input.
        computations_requested (List[ComputationRequested]): List of computations that were requested.
        computations_results (List[ComputationResult]): List of results for completed computations.
    """

    type: Literal['brain.input.clarification'] = 'brain.input.clarification'
    computations_requested: List[ComputationRequested] = []
    computations_results: List[ComputationResult] = []


BrainInput = Union[
    BrainInputFresh,
    BrainInputResults,
]
"""Union type representing all possible Brain input variants."""


BrainInputAdapter: TypeAdapter[BrainInput] = TypeAdapter(
    Annotated[
        BrainInput,
        Field(discriminator='type')
    ]
)
"""Type adapter for serializing/deserializing BrainInput instances."""


class BrainOutputBase(BaseModel):
    """Base class for all Brain output types.

    Attributes:
        token_usage (Optional[TokenUsage]): Optional usage statistics for token consumption.
    """

    token_usage: Optional[TokenUsage]


class BrainOutputResponse(BrainOutputBase):
    """Represents a Brain output containing a text-based response.

    Attributes:
        type (Literal['brain.output.response']): The fixed type discriminator for this output.
        message (AgentMessage): The agent's message to the recipient.
    """

    type: Literal['brain.output.response'] = 'brain.output.response'
    message: AgentMessage


class BrainOutputResponseStructured(BrainOutputBase):
    """Represents a Brain output with structured data payload.

    Attributes:
        type (Literal['brain.output.structured']): The fixed type discriminator for this output.
        message_id (str): Identifier for the message.
        payload (Dict[str, Any]): Arbitrary structured data.
        structure (str): The schema or structure name for the payload.
    """

    type: Literal['brain.output.structured'] = 'brain.output.structured'
    message_id: str
    payload: Dict[str, Any]
    structure: str


class BrainOutputContribution(BrainOutputBase):
    """Represents a Brain output containing a contribution message.

    Attributes:
        type (Literal['brain.output.contribution']): The fixed type discriminator for this output.
        message (AgentMessage): The agent's contribution message.
    """

    type: Literal['brain.output.contribution'] = 'brain.output.contribution'
    message: AgentMessage


class BrainOutputComputationsRequired(BrainOutputBase):
    """Represents a Brain output that requires computations to be performed.

    Attributes:
        type (Literal['brain.output.computations']): The fixed type discriminator for this output.
        computations_required (List[ComputationRequested]): List of computations that need to be performed.
    """

    type: Literal['brain.output.computations'] = 'brain.output.computations'
    computations_required: List[ComputationRequested]


BrainOutput = Union[
    BrainOutputComputationsRequired,
    BrainOutputContribution,
    BrainOutputResponse,
    BrainOutputResponseStructured,
]
"""Union type representing all possible Brain output variants."""


BrainOutputAdapter: TypeAdapter[BrainOutput] = TypeAdapter(
    Annotated[
        BrainOutput,
        Field(discriminator='type')
    ]
)
"""Type adapter for serializing/deserializing BrainOutput instances."""


SituationBuilderFn = Callable[
    [BrainInputBase, RunnableConfig],
    str
]
"""Callable type for functions that build a situation description.

Args:
    input_data (BrainInputBase): The base input to process.
    config (RunnableConfig): Configuration for the runnable environment.

Returns:
    (str): The constructed situation description.
"""


InstructionsTransformerFn = Callable[
    [str, BrainInputBase, RunnableConfig],
    str
]
"""Callable type for functions that transform instructions.

Args:
    instructions (str): The raw instruction string to transform.
    input_data (BrainInputBase): The base input to process.
    config (RunnableConfig): Configuration for the runnable environment.

Returns:
    (str): The transformed instruction string.
"""