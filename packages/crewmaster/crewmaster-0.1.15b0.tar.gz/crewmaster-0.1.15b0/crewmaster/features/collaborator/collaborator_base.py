"""Base classes for collaborator components in Crewmaster.

This module defines the foundational classes for creating and managing a
"collaborator" within a crew. It provides an abstract base class `CollaboratorBase`
that handles state management, graph setup, and async invocation/streaming.
"""

from abc import (
    abstractmethod
)
from typing import (
    Any,
    AsyncIterator,
    Dict,
    List,
    Optional,
    cast,
)
import structlog

from langchain_core.runnables import (
    RunnableConfig,
)
from langchain_core.runnables.utils import (
    ConfigurableFieldSpec
)
from langchain_openai import ChatOpenAI
from ...core.pydantic import (
    BaseModel,
)
from langgraph.graph.state import (
    CompiledStateGraph,
    StateGraph,
)
from langchain_core.callbacks.manager import (
    CallbackManagerForChainRun
)
from ..runnables import (
    RunnableStreameable,
    WithAsyncStreamConfigVerified,
    WithAsyncInvokeConfigVerified,
)

from .team_membership import (
    TeamMembership,
)
from .collaborator_ouput import (
    CollaboratorOutput,
)
from .collaborator_input import (
    CollaboratorInput,
    CollaboratorInputFresh,
    CollaboratorInputClarification,
)
from .types import (
    CollaboratorConfig,
)
from .state import (
    CollaboratorState
)


log = structlog.get_logger()
"Loger para el módulo"


class CollaboratorBase(
    WithAsyncInvokeConfigVerified[CollaboratorInput, CollaboratorOutput],
    WithAsyncStreamConfigVerified[CollaboratorInput, CollaboratorOutput],
    RunnableStreameable[CollaboratorInput, CollaboratorOutput]
):
    """Abstract base class for all collaborator components.

    This class provides a foundational structure for any collaborator in the
    Crewmaster system. Collaborators are runnable units that can be part of a team
    and handle specific jobs.

    Attributes:
        job_description (str): A description of the collaborator's responsibility.
    """
    job_description: str
    """Responsabilidad del colaborador"""

    @property
    def config_specs(self) -> List[ConfigurableFieldSpec]:
        """Required fields in the configuration for this runnable.

        Returns:
            (list): A list of ConfigurableFieldSpec objects.
        """
        return [
            ConfigurableFieldSpec(
                id='llm_srv',
                name='LLM para consultar',
                description=(
                    'Servicio para conectarse con un LLM provider,'
                ),
                annotation=ChatOpenAI,
                default=...
            ),
            ConfigurableFieldSpec(
                id='user_name',
                name='Usuario logueado',
                description=(
                    'Usuario logueado en la aplicación'
                ),
                annotation=str,
                default=...
            ),
            ConfigurableFieldSpec(
                id='today',
                name='Fecha actual',
                description=(
                    'Fecha en formato Iso'
                ),
                annotation=str,
                default=...
            )
        ]
    """Campos requeridos en la configuración de este runnable"""

    @abstractmethod
    def join_team(
        self,
        team_membership: TeamMembership
    ):
        """Abstract method to make the collaborator join a team.

        Args:
            team_membership (TeamMembership): The team membership details to join.
        """
        pass

    @abstractmethod
    def _build_graph(
        self,
        graph: StateGraph,
        config_parsed: BaseModel,
        config_raw: RunnableConfig,
    ) -> StateGraph:
        """Builds the state graph for the collaborator's logic.

        This method must be implemented by all subclasses.

        Args:
            graph (StateGraph): The initial state graph to build upon.
            config_parsed (BaseModel): The parsed configuration.
            config_raw (RunnableConfig): The raw runnable configuration.

        Returns:
            StateGraph: The built state graph.
        """
        pass

    def invoke(
        self,
        input: CollaboratorInput,
        config: RunnableConfig | None = None
    ) -> CollaboratorOutput:
        """Invokes the collaborator.

        Raises:
            Exception: Collaborator can only be called asynchronously.
        """
        raise Exception('Collaborator can only be called asynchronously')

    def _setup_graph(
        self,
        config_parsed: BaseModel,
        config_raw: RunnableConfig,
    ) -> CompiledStateGraph:
        """Initializes and compiles the state graph.

        Args:
            config_parsed (BaseModel): The parsed configuration.
            config_raw (RunnableConfig): The raw runnable configuration.

        Returns:
            CompiledStateGraph: The compiled state graph.
        """
        init_graph = StateGraph(
            state_schema=CollaboratorState,
            config_schema=CollaboratorConfig,
        )
        prepared = self._build_graph(
            graph=init_graph,
            config_parsed=config_parsed,
            config_raw=config_raw
        )
        compiled = prepared.compile()
        compiled.stream_channels = ["cleaner"]

        return compiled

    def _rebuild_state(
        self,
        input: CollaboratorInput,
        config_parsed: BaseModel,
        config_raw: RunnableConfig,
    ) -> CollaboratorState:
        """Rebuilds the collaborator's state from the input.

        Args:
            input (CollaboratorInput): The input data for the collaborator.
            config_parsed (BaseModel): The parsed configuration.
            config_raw (RunnableConfig): The raw runnable configuration.

        Raises:
            ValueError: If the type of input is not valid.

        Returns:
            CollaboratorState: The rebuilt collaborator state.
        """
        if isinstance(input, CollaboratorInputFresh):
            state = CollaboratorState(
                public_messages=input.public_messages,
                private_messages=input.private_messages,
                fresh_message=input.message
            )
            return state
        if isinstance(input, CollaboratorInputClarification):
            context = input.clarification_message.clarification_context
            state = CollaboratorState(
                public_messages=input.public_messages,
                private_messages=input.private_messages,
                computations_requested=context.computations_requested,
                computations_results=context.computations_results,
                fresh_message=input.clarification_message
            )
            return state
        # Si llegamos hasta aquí es un tipo desconocido de entrada
        raise ValueError(
            f'Type of input is not valid. received={input.type}'
        )

    def _output_acl(
        self,
        state: Dict[str, Any],
        config_parsed: BaseModel,
        config_raw: RunnableConfig
    ) -> CollaboratorOutput:
        """Validates the state output and casts it to CollaboratorOutput.

        Args:
            state (dict): The state dictionary returned by the graph.
            config_parsed (BaseModel): The parsed configuration.
            config_raw (RunnableConfig): The raw runnable configuration.

        Raises:
            ValueError: If the state.output is invalid.

        Returns:
            CollaboratorOutput: The casted output.
        """
        # The graph always returns the state as a Dictionary
        # For that reason we can't type the received state as CrewState
        result = state.get("output")
        if result is None:
            raise ValueError('Invalid state.output on output_acl')
        result = cast(CollaboratorOutput, result)
        return result

    def _build_config(
        self,
        config_raw: RunnableConfig
    ) -> RunnableConfig:
        """Builds the runnable configuration.

        Args:
            config_raw (RunnableConfig): The raw runnable configuration.

        Returns:
            RunnableConfig: The configured runnable.
        """
        return config_raw

    async def async_invoke_config_parsed(
        self,
        input: CollaboratorInput,
        config_parsed: BaseModel,
        config_raw: RunnableConfig
    ) -> CollaboratorOutput:
        """Asynchronously invokes the collaborator with a parsed configuration.

        Args:
            input (CollaboratorInput): The input data for the collaborator.
            config_parsed (BaseModel): The parsed configuration.
            config_raw (RunnableConfig): The raw runnable configuration.

        Returns:
            CollaboratorOutput: The output of the collaborator.
        """
        graph = self._setup_graph(
            config_parsed=config_parsed,
            config_raw=config_raw
        )
        state = self._rebuild_state(
            input=input,
            config_parsed=config_parsed,
            config_raw=config_raw
        )
        config_tunned = self._build_config(config_raw)
        graph_result = await graph.ainvoke(
            state,
            config_tunned
        )
        result = self._output_acl(
            graph_result,
            config_parsed=config_parsed,
            config_raw=config_raw
        )
        return result

    async def astream_config_parsed(
        self,
        input: CollaboratorInput,
        config_parsed: BaseModel,
        config_raw: RunnableConfig,
        run_manager: CallbackManagerForChainRun,
        **kwargs: Optional[Any],
    ) -> AsyncIterator[Dict[str, Any]]:
        """Asynchronously streams the output of the collaborator.

        Args:
            input (CollaboratorInput): The input data for the collaborator.
            config_parsed (BaseModel): The parsed configuration.
            config_raw (RunnableConfig): The raw runnable configuration.
            run_manager (CallbackManagerForChainRun): The run manager.
            **kwargs: Optional keyword arguments.

        Yields:
            (dict): The chunks of the output.
        """
        graph = self._setup_graph(
            config_parsed=config_parsed,
            config_raw=config_raw
        )
        state = self._rebuild_state(
            input=input,
            config_parsed=config_parsed,
            config_raw=config_raw
        )
        config_tunned = self._build_config(config_raw)
        iterator = graph.astream(
            state,
            config_tunned,
            output_keys='output'
        )
        async for chunk in iterator:
            yield chunk
