"""
Module for the BrainBase core logic in CrewMaster.

This module defines the `BrainBase` class and its associated utility functions.
It provides the building blocks for constructing, invoking, and processing
messages between the CrewMaster "Brain" and external components, including
LLM-based agents and computation tools.
"""

from typing import (
    Any,
    AsyncIterator,
    Dict,
    List,
    Optional,
    cast,
)
from ...core.pydantic import (
    model_validator,
    BaseModel,
)
from langchain_core.utils.aiter import aclosing

import structlog
from langchain_openai import ChatOpenAI
from langchain_core.runnables import (
    RunnableConfig,
)
from langchain.agents.output_parsers.openai_tools import (
    OpenAIToolsAgentOutputParser
)
from langchain_core.messages import (
    AIMessage,
    ToolMessage,
    BaseMessage,
    AIMessageChunk,
)
from langchain_core.runnables.utils import (
    ConfigurableFieldSpec
)
from langchain_core.agents import (
    AgentFinish,
    AgentAction,
)
from langchain_core.prompt_values import (
    PromptValue,
)
from langchain.agents.output_parsers.tools import (
    ToolAgentAction
)
from langchain_core.messages.tool import (
    ToolCall
)
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_core.callbacks.manager import (
    CallbackManagerForChainRun
)
from ..runnables import (
    WithInvokeConfigVerified,
    WithAsyncStreamConfigVerified,
    RunnableStreameable,
)
from ..helpers import (
    check_templates_for_valid_placeholders
)
from ..collaborator import (
    AgentMessage,
    HistoryStrategyInterface,
    MaxMessagesStrategy,
    TokenUsage,
)
from ..skill import (
    ComputationRequested,
    ComputationResult,
    Skill,
    SkillStructuredResponse,
)
from .brain_types import (
    BrainInput,
    BrainInputBase,
    BrainInputResults,
    BrainOutput,
    BrainOutputComputationsRequired,
    BrainOutputContribution,
    BrainOutputResponse,
    BrainOutputResponseStructured,
    InstructionsTransformerFn,
    SituationBuilderFn,
)


log = structlog.get_logger()
"Loger para el módulo"


def ensure_dict(
    candidate: str | Dict[str, Any],
    key: str = 'input'
) -> Dict[str, Any]:
    """Ensures that the given candidate is a dictionary.

    If a string is provided, it will be wrapped in a dictionary under the
    specified key.

    Args:
        candidate: A string or dictionary to validate.
        key: The key to use if `candidate` is a string.

    Returns:
        Dict[str, Any]: The resulting dictionary.
    """
    if isinstance(candidate, str):
        candidate = {key: candidate}
    return candidate


def convert_action_to_computation(
    action: AgentAction
) -> ComputationRequested:
    """Converts an agent action to a computation request.

    Args:
        action: The `AgentAction` instance to convert.

    Returns:
        ComputationRequested: A computation request built from the action.
    """
    tool_call_id = action.tool_call_id if (
        isinstance(action, ToolAgentAction)
     ) else ''
    tool_input = action.tool_input if (
                    isinstance(action.tool_input, Dict)
                ) else {"value": action.tool_input}
    result = ComputationRequested(
        name=action.tool,
        computation_id=tool_call_id,
        brain_args=tool_input
    )
    return result


def is_response_structured(
    name: str,
    skills: List[Skill]
):
    """Checks if a Skill with the given name is of type `SkillStructuredResponse`.

    Args:
        name: The name of the skill to check.
        skills: A list of `Skill` instances.

    Returns:
        bool: True if a skill with the given name exists and is of type
        `SkillStructuredResponse`, otherwise False.
    """
    return any(
        skill.name == name and
        isinstance(skill, SkillStructuredResponse)
        for skill in skills
    )


def convert_to_tool_message(
    value: ComputationResult
) -> ToolMessage:
    """Converts a computation result to a `ToolMessage`.

    Args:
        value: The computation result to convert.

    Returns:
        ToolMessage: A tool message containing the computation result.
    """
    converted = ToolMessage(
        name=value.name,
        tool_call_id=value.computation_id,
        content=str(value.result)
    )
    return converted


def convert_to_tool_call(
    value: ComputationResult
) -> ToolCall:
    """Converts a computation result to a `ToolCall`.

    Args:
        value: The computation result to convert.

    Returns:
        ToolCall: A tool call representing the computation request.
    """
    result = ToolCall(
        name=value.name,
        args=value.skill_args.model_dump(),
        id=value.computation_id
    )
    return result


class BrainBase(
    WithInvokeConfigVerified[BrainInput, BrainOutput],
    WithAsyncStreamConfigVerified[BrainInput, BrainOutput],
    RunnableStreameable[BrainInput, BrainOutput]
):
    """Base class for implementing Brain components in CrewMaster.

    This class provides mechanisms to:
    * Build prompts for LLMs
    * Parse actions and outputs from LLMs
    * Handle both synchronous and asynchronous execution
    * Manage skill registration and configuration

    Attributes:
        name: The name of this brain component.
        instructions: Base instructions for the LLM.
        agent_name: The agent's identifier name.
        situation_builder: Optional callable for building context situations.
        skills: A list of skills available to the brain.
        history_strategy: Strategy for managing conversation history.
        instructions_transformer: Optional callable for modifying instructions before sending to LLM.
    """
    name: str = "brain"
    instructions: str
    agent_name: str
    situation_builder: Optional[SituationBuilderFn] = None

    skills: List[Skill] = []
    history_strategy: HistoryStrategyInterface = MaxMessagesStrategy()
    instructions_transformer: Optional[InstructionsTransformerFn] = None

    @property
    def config_specs(self) -> List[ConfigurableFieldSpec]:
        """Returns the list of configurable fields for this runnable.

        Returns:
            List[ConfigurableFieldSpec]: The configuration specifications.
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
            )
        ]

    @model_validator(mode='before')
    def validate_templates(cls, values):
        """Validates that all template placeholders in instructions are valid.

        Args:
            values: The values passed to the model.

        Returns:
            dict: The validated values.
        """
        templates_properties = [
            'instructions'
        ]
        brain_input_fields = BrainInputBase.model_fields.keys()
        return check_templates_for_valid_placeholders(
            source=values,
            properties_using_templates=templates_properties,
            availables_keys=brain_input_fields
        )

    def _build_messages_for_llm(
        self,
        input: BrainInput,
        config: RunnableConfig,
    ) -> PromptValue:
        """Builds the messages to be sent to the LLM based on the input and config.

        Args:
            input: The brain input.
            config: The runnable configuration.

        Returns:
            PromptValue: The prompt to send to the LLM.
        """
        situation = ''
        if self.situation_builder is not None:
            situation = self.situation_builder(input, config)

        instructions_with_situation = self.instructions + situation
        if self.instructions_transformer is not None:
            instructions_with_situation = self.instructions_transformer(
                instructions_with_situation,
                input,
                config
            )
        system_message = SystemMessagePromptTemplate.from_template(
            instructions_with_situation
        )

        history = input.messages
        history_summary = self.history_strategy.execute(history)

        # Buscamos los mensajes de tool para pasarlos como Mensajes al LLM
        computation_messages = []
        if isinstance(input, BrainInputResults):
            results = input.computations_results
            tools_messages = [convert_to_tool_message(result)
                              for result in results]
            tools_calls = [convert_to_tool_call(result)
                           for result in results]
            tool_request = AIMessage(
                tool_calls=tools_calls,
                content=''
            )
            computation_messages = [tool_request] + tools_messages

        context = ChatPromptTemplate.from_messages(
            [system_message] + history_summary + computation_messages
        )
        input_as_dict = dict(input)
        result = context.invoke(input_as_dict, config)
        return result

    def _parse_actions(
        self,
        message: BaseMessage
    ) -> BrainOutput:
        """Parses actions from an LLM output message into a BrainOutput.

        Args:
            message: The message returned by the LLM.

        Returns:
            BrainOutput: The parsed output.
        """
        usage = message.usage_metadata if (
                            isinstance(message, AIMessage)
                        ) else None
        token_usage = TokenUsage.model_validate(
                                    usage
                                ) if usage is not None else None
        actions_or_finish = OpenAIToolsAgentOutputParser().invoke(message)
        if isinstance(actions_or_finish, AgentFinish):
            finish = actions_or_finish
            message = AgentMessage(
                content=finish.return_values.get('output', ''),
                to='user',
                author=self.agent_name
            )
            result = BrainOutputResponse(
                message=message,
                token_usage=token_usage
            )
            return result

        actions = actions_or_finish
        contributions = [action for action in actions
                         if action.tool == 'send_message_to_colleague']
        if len(contributions) > 0:
            contribution_tool = contributions[0]
            if isinstance(contribution_tool.tool_input, str):
                raise ValueError('Invalid tool_input for Contribution')
            contribution_input = contribution_tool.tool_input or {}
            content = contribution_input.get("message", "")
            to = contribution_input.get("to", "")
            message = AgentMessage(
                content=content,
                to=to,
                author=self.agent_name
            )
            return BrainOutputContribution(
                message=message,
                token_usage=token_usage
            )

        structured = [action for action in actions
                      if is_response_structured(action.tool, self.skills)]
        if len(structured) > 0:
            response = cast(ToolAgentAction, structured[0])
            tool_input = ensure_dict(response.tool_input)
            return BrainOutputResponseStructured(
                payload=tool_input,
                structure=response.tool,
                message_id=response.tool_call_id,
                token_usage=token_usage
            )
        computations = [convert_action_to_computation(action)
                        for action in actions]
        return BrainOutputComputationsRequired(
            computations_required=computations,
            token_usage=token_usage
        )

    def _setup_llm(
        self,
        config_parsed: BaseModel,
    ):
        """Configures the LLM with the registered tools.

        Args:
            config_parsed: The parsed configuration.

        Returns:
            Any: The LLM instance bound with tools.
        """
        configurable = getattr(config_parsed, "configurable")
        llm_srv = cast(ChatOpenAI, getattr(configurable, "llm_srv"))
        tools = [skill.as_tool() for skill in self.skills]
        llm_with_tools = llm_srv.bind_tools(tools)
        return llm_with_tools

    def invoke_config_parsed(
        self,
        input: BrainInput,
        config_parsed: BaseModel,
        config_raw: RunnableConfig
    ) -> BrainOutput:
        """Synchronously invokes the brain with parsed configuration.

        Args:
            input: The brain input.
            config_parsed: The parsed configuration model.
            config_raw: The raw configuration.

        Returns:
            BrainOutput: The brain's output.
        """
        # configuramos el llm con los tools
        llm_with_tools = self._setup_llm(config_parsed=config_parsed)
        # Construimos los mensajes que se van a enviar al LLM
        messages_to_llm = self._build_messages_for_llm(input, config_raw)
        # Ejecutamos el llm
        result_llm = llm_with_tools.invoke(messages_to_llm, config_raw)
        # Transformamos el resultado
        result = self._parse_actions(result_llm)
        return result

    async def astream_config_parsed(
        self,
        input: BrainInput,
        config_parsed: BaseModel,
        config_raw: RunnableConfig,
        run_manager: CallbackManagerForChainRun,
        **kwargs: Optional[Any],
    ) -> AsyncIterator[BaseMessage]:
        """Asynchronously streams output from the brain with parsed configuration.

        Args:
            input: The brain input.
            config_parsed: The parsed configuration model.
            config_raw: The raw configuration.
            run_manager: The run manager for handling callbacks.
            **kwargs: Additional keyword arguments.

        Yields:
            BaseMessage: Each chunk of streamed LLM output.
        """
        # configuramos el llm con los tools
        llm_with_tools = self._setup_llm(config_parsed=config_parsed)
        # Construimos los mensajes que se van a enviar al LLM
        messages_to_llm = self._build_messages_for_llm(input, config_raw)
        iterator = llm_with_tools.astream(
            messages_to_llm,
            config_raw,
        )
        complete_response: BaseMessage = AIMessageChunk(content='')
        async with aclosing(iterator):
            async for chunk in iterator:
                complete_response += chunk
                yield chunk
        result = self._parse_actions(complete_response)
        run_manager.on_chain_end(result)

    def get_skills_as_dict(
        self
    ) -> Dict[str, Skill]:
        """Returns the registered skills as a dictionary keyed by skill name.

        Returns:
            Dict[str, Skill]: Mapping from skill name to skill object.
        """
        skills = self.skills
        skill_map: Dict[
            str, Skill
        ] = {skill.name: skill
             for skill in skills}
        return skill_map
