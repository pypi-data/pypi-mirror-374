"""A custom JSON serializer for LangChain's LangGraph library.

This module provides a custom serializer that extends JsonPlusSerializer to
correctly handle serialization and deserialization of custom Pydantic models
defined within the crewmaster library. This is necessary because LangGraph
needs to know about these custom namespaces to correctly revive objects.
"""

import importlib
from typing import Any, List, Optional
from langchain_core.load.load import Reviver
from langgraph.checkpoint.serde.jsonplus import (
    JsonPlusSerializer
)
import structlog

log = structlog.get_logger()
"Loger para el módulo"

SERIALIZER_VALID_NAMESPACES = ['crewmaster']


class JsonSerializarFromCustomModels(JsonPlusSerializer):
    """A JSON serializer for custom Crewmaster models.

    This class extends the `JsonPlusSerializer` to properly handle custom
    models from the `crewmaster` namespace. It ensures that LangChain's
    `Reviver` is aware of the `crewmaster` modules, preventing errors
    during deserialization of checkpoints.
    """
    reviver: Reviver

    def __init__(
        self,
        *args,
        valid_namespaces: Optional[List[str]] = SERIALIZER_VALID_NAMESPACES,
        **kwargs
    ):
        """Initializes the serializer with a list of valid namespaces.

        Args:
            *args: Variable length argument list.
            valid_namespaces (list): The list of namespaces to validate.
            **kwargs: Arbitrary keyword arguments.
        """        
        super().__init__(*args, **kwargs)
        self.reviver = Reviver(valid_namespaces=valid_namespaces)

    def _reviver(self, value: dict[str, Any]) -> Any:
        """Revives a serialized object into a Python object.

        This method checks for the standard LangChain serialization format and
        attempts to load the object from the valid namespaces.
        
        If the format is not recognized, it falls back to the reviver
        with the valid_namespaces configured.

        Args:
            value (dict): The dictionary containing the serialized object data.

        Returns:
            (Any): The deserialized Python object or the original value
                if it could not be deserialized.
        """
        if (
            value.get("lc", None) == 2
            and value.get("type", None) == "constructor"
            and value.get("id", None) is not None
        ):
            return super()._reviver(value)
        # For other objects, uses the default reviver
        # with the valid_namespaces including "crewmaster"
        return self.reviver(value)
