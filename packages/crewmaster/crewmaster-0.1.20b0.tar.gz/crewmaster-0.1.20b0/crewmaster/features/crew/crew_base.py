
from typing import (
    Any,
    AsyncIterator,
    Dict,
    Literal,
    cast,
    List,
)
import structlog
from ...core.pydantic import (
    BaseModel,
)
from langchain_core.runnables import (
    RunnableConfig,
)
from langchain_core.runnables.config import (
    merge_configs,
)
from langgraph.graph.state import (
    StateGraph,
    CompiledStateGraph,
)
from langchain_core.callbacks.manager import (
    CallbackManagerForChainRun
)
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
)
from langchain_core.runnables.utils import (
    ConfigurableFieldSpec,
    get_unique_config_specs,
)
from ..runnables import (
    WithAsyncStreamConfigVerified,
    WithAsyncInvokeConfigVerified,
    RunnableStreameable,
)
from .state import (
    CrewState
)
from ..team import (
    TeamBase,
)
from ..collaborator import (
    CollaboratorInputClarification,
    CollaboratorInputFresh,
    CollaboratorOutputResponse,
    CollaboratorOutputResponseStructured,
    CollaboratorOutputClarification,
    ClarificationMessage,
    ClarificationContext,
)
from .types import (
    CrewConfig,
    ClarificationPending,
)
from .crew_input import (
    CrewInput,
    CrewInputClarification,
    CrewInputFresh,
)
from .crew_output import (
    CrewOutput,
)


log = structlog.get_logger()
"Loger para el módulo"


def team_node(
    team: TeamBase
):
    """
    Creates an executor node for handling Crew interactions with a Team.

    This node converts Crew input into the appropriate Team input
    (either a fresh message or a clarification) and invokes the Team.

    Args:
        team (TeamBase): The team instance that will handle the input.

    Returns:
        (Callable[[CrewState, RunnableConfig], dict]): An async executor function.

    Raises:
        ValueError: If CrewState input type is invalid or if a clarification
            does not match the pending clarification.
    """
    async def executor(
        state: CrewState,
        config: RunnableConfig
    ):
        if isinstance(state.input, CrewInputClarification):
            received = state.input.clarification_message
            pending = state.clarification
            if pending is None:
                raise ValueError('There is no clarification pending')
            if pending.requested.clarification_id != received.computation_id:
                raise ValueError(
                    'There is no clarification '
                    f'with id={received.computation_id}'
                )
            # Tenemos una clarificación pendiente con el mismo id recibido
            saved_context = pending.context
            context = ClarificationContext(
                computations_requested=saved_context.computations_requested,
                computations_results=saved_context.computations_results,
                requested_by=saved_context.requested_by
            )
            simple = state.input.clarification_message
            clarification_message = ClarificationMessage(
                to=context.requested_by,
                payload=simple.payload,
                timestamp=simple.timestamp,
                computation_id=simple.computation_id,
                clarification_context=context,
                content=""
            )
            team_input = CollaboratorInputClarification(
                clarification_message=clarification_message,
                public_messages=state.public_messages
            )
        elif isinstance(state.input, CrewInputFresh):
            team_input = CollaboratorInputFresh(
                public_messages=state.public_messages,
                message=state.input.message
            )
        else:
            raise ValueError('Invalid Crew State Input type')
        default_config = RunnableConfig(
            run_name="cbr:team",
            tags=["cbr:team"],
            metadata={
                "cbr_team_name": team.name
            }
        )
        merged_config = merge_configs(default_config, config)
        result = await team.ainvoke(team_input, merged_config)
        return {
            "output": result
        }

    return executor


def cleaner(
    state: CrewState,
    config: RunnableConfig
):
    """
    Final node in the Crew graph for cleaning up and updating message history.

    Adds fresh user messages to the public messages and stores
    responses or clarifications from collaborators.  

    Args:
        state (CrewState): The current state of the Crew execution.
        config (RunnableConfig): The configuration used for this execution.

    Returns:
        (dict): Updated state containing either public messages or pending clarification.

    Raises:
        ValueError: If the output is not a recognized CollaboratorOutput type.
    """
    # Buscamos los mensajes anteriores
    public_messages = state.public_messages
    # Evaluamos el fresh_message recibido
    input = state.input
    # Agregamos el fresh_message sólo si viene del Usuario.
    # No se agregan los clarification_messages
    if isinstance(input, CrewInputFresh):
        public_messages += [input.message]
    # Evaluamos el output
    output = state.output
    # Agregamos la salida sólo si es Response o ResponseStructured
    if isinstance(
        output,
        (CollaboratorOutputResponse, CollaboratorOutputResponseStructured)
    ):
        # Almacenamos la respuesta en la historia de mensajes
        fresh_response = output.message
        public_messages += [fresh_response]
        return {
            "public_messages": public_messages,
            "private_messages": []
        }
    if isinstance(
        output,
        CollaboratorOutputClarification
    ):
        pending = ClarificationPending(
                requested=output.clarification_requested,
                context=output.clarification_context
        )
        # Debemos establecer el contexto
        return {
            "public_messages": public_messages,
            "clarification": pending
        }
    raise ValueError('Invalid Collaborator Output in cleaner')


class CrewBase(
    WithAsyncInvokeConfigVerified[CrewInput, CrewOutput],
    WithAsyncStreamConfigVerified[CrewInput, CrewOutput],
    RunnableStreameable[CrewInput, CrewOutput]
):
    """
    Base class for managing a Crew with asynchronous invocation and streaming.

    Handles interaction with a Team and manages Crew state, inputs, and outputs.

    Attributes:
        team (TeamBase): The team assigned to this Crew instance.
    """
    team: TeamBase

    @property
    def config_specs(self) -> List[ConfigurableFieldSpec]:
        """
        Returns all configuration dependencies required by the Crew and its Team.

        Returns:
            List[ConfigurableFieldSpec]: Unique configuration specifications
            for the Crew and Team.
        """
        crew = [
            ConfigurableFieldSpec(
                id='checkpointer',
                name='Checkpointer para persistencia',
                description=(
                    'Servicio para persistencia del graph'
                ),
                annotation=BaseCheckpointSaver,
                default=...
            ),
            ConfigurableFieldSpec(
                id='thread_id',
                name='Identificador del thread',
                description=(
                    'Thread id para persistencia'
                ),
                annotation=str,
                default=...
            ),
        ]
        team = self.team.config_specs
        combined = crew + team
        return get_unique_config_specs(combined)

    def invoke(
        self,
        input: CrewInput,
        config: RunnableConfig | None = None
    ) -> CrewOutput:
        """
        Synchronous invocation is not supported; Crew must be invoked asynchronously.

        Raises:
            Exception: Always raises because synchronous calls are not allowed.
        """
        raise Exception('Crew can only be called asynchronously')

    def _setup_graph(
        self,
        checkpointer: BaseCheckpointSaver,
    ) -> CompiledStateGraph:
        """
        Constructs and compiles the Crew execution graph.

        Args:
            checkpointer (BaseCheckpointSaver): Service used for graph persistence.

        Returns:
            CompiledStateGraph: The compiled Crew graph ready for async execution.
        """
        graph = StateGraph(
            state_schema=CrewState,
            config_schema=CrewConfig,
        )
        graph.add_node('team', team_node(self.team))  # type: ignore
        graph.add_node(cleaner)                       # type: ignore
        graph.set_entry_point('team')
        graph.add_edge('team', 'cleaner')
        graph.set_finish_point('cleaner')
        compiled = graph.compile(
            checkpointer=checkpointer
        )
        return compiled

    def _rebuild_state(
        self,
        input: CrewInput,
        config_parsed: BaseModel,
        config_raw: RunnableConfig
    ) -> Dict[Literal["input"], CrewInput]:
        """
        Converts raw input into a CrewState-compatible dictionary.

        Args:
            input (CrewInput): Input for the Crew.
            config_parsed (BaseModel): Parsed configuration object.
            config_raw (RunnableConfig): Raw configuration object.

        Returns:
            dict: State dictionary containing the input under the key "input".
        """
        return {
            "input": input
        }

    def _output_acl(
        self,
        state: Dict[str, Any],
        config_parsed: BaseModel,
        config_raw: RunnableConfig
    ) -> CrewOutput:
        """
        Extracts and validates the output from the Crew graph state.

        Args:
            state (dict): Current state from graph execution.
            config_parsed (BaseModel): Parsed configuration object.
            config_raw (RunnableConfig): Raw configuration object.

        Returns:
            CrewOutput: Output result of the Crew execution.

        Raises:
            ValueError: If the output in the state is missing or invalid.
        """
        # El graph siempre devuelve el estado como un Diccionario
        # Por esa razón no podemos tipear el state recibido
        # como CrewState
        result = state.get("output")
        if result is None:
            raise ValueError('Invalid state.output on output_acl')
        result = cast(CrewOutput, result)

        return result

    def _build_config(
        self,
        config_raw: RunnableConfig
    ) -> RunnableConfig:
        """
        Merges the default Crew configuration with a provided raw configuration.

        Args:
            config_raw (RunnableConfig): The raw configuration to merge.

        Returns:
            RunnableConfig: The final merged configuration.
        """
        default_config = RunnableConfig(
            run_name="cbr:crew",
            tags=["cbr:crew"]
        )
        merged_config = merge_configs(default_config, config_raw)
        return merged_config

    async def async_invoke_config_parsed(
        self,
        input: CrewInput,
        config_parsed: BaseModel,
        config_raw: RunnableConfig
    ) -> CrewOutput:
        """
        Asynchronously invokes the Crew graph using a parsed configuration.

        Args:
            input (CrewInput): Input data for the Crew.
            config_parsed (BaseModel): Fully parsed configuration.
            config_raw (RunnableConfig): Raw configuration data.

        Returns:
            CrewOutput: Output from the Crew after execution.
        """
        # Aquí estoy seguro que el config_parsed
        # tiene todos los campos que le pedí en config_specs
        # No puedo pedirlo directamente porque no tengo forma de tipearlo
        configurable = getattr(config_parsed, "configurable")
        checkpointer = getattr(configurable, "checkpointer")
        # Preparamos el graph con el checkpointer
        graph = self._setup_graph(
            checkpointer=checkpointer
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
        input: CrewInput,
        config_parsed: BaseModel,
        config_raw: RunnableConfig,
        run_manager: CallbackManagerForChainRun,
        **kwargs: Any,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Streams Crew execution results asynchronously using a parsed configuration.

        Args:
            input (CrewInput): Input for the Crew.
            config_parsed (BaseModel): Parsed configuration object.
            config_raw (RunnableConfig): Raw configuration object.
            run_manager (CallbackManagerForChainRun): Callback manager for streaming.
            **kwargs: Additional parameters for the streaming executor.

        Yields:
            AsyncIterator[dict]: Streamed chunks of execution state containing output.
        """
        # Aquí estoy seguro que el config_parsed
        # tiene todos los campos que le pedí en config_specs
        # No puedo pedirlo directamente porque no tengo forma de tipearlo
        configurable = getattr(config_parsed, "configurable")
        checkpointer = getattr(configurable, "checkpointer")
        # Preparamos el graph con el checkpointer
        graph = self._setup_graph(
            checkpointer=checkpointer
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
            output_keys='output',
            **kwargs
        )
        async for chunk in iterator:
            yield chunk
