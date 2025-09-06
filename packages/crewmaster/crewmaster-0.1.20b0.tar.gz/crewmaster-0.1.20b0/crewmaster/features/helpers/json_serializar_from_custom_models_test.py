import structlog
from datetime import datetime
import pytest

from ..collaborator.message import UserMessage
from .json_serializar_from_custom_models import JsonSerializarFromCustomModels
from langgraph.checkpoint.serde.jsonplus import (
    JsonPlusSerializer
)

log = structlog.get_logger()
"Loger para el módulo"

def test_serializer_with_simple_values() -> None:
    to_serialize = 'pedrito'
    serde = JsonSerializarFromCustomModels()
    dumped = serde.dumps(to_serialize)
    assert serde.loads(dumped) == to_serialize    

def test_serializer() -> None:
    """Inspired on: https://github.com/langchain-ai/langgraph/blob/d503c0bf3303a97e1eaec0eabe7ab6f219df62ec/libs/checkpoint/tests/test_jsonplus.py#L91"""
    user_message = UserMessage(
        content="mensaje de prueba",
        timestamp=datetime.now().isoformat()
    )
    to_serialize = { "message": user_message }
    serde = JsonSerializarFromCustomModels()
    dumped = serde.dumps(to_serialize)
    assert serde.loads(dumped) == to_serialize
    for value in to_serialize.values():
        assert serde.loads(serde.dumps(value)) == value

def test_serializer_typed() -> None:
    """Inspired on: https://github.com/langchain-ai/langgraph/blob/d503c0bf3303a97e1eaec0eabe7ab6f219df62ec/libs/checkpoint/tests/test_jsonplus.py#L91"""
    user_message = UserMessage(
        content="mensaje de prueba",
        timestamp=datetime.now().isoformat()
    )
    to_serialize = { "message": user_message }

    serde = JsonSerializarFromCustomModels()

    dumped = serde.dumps_typed(to_serialize)

    assert serde.loads_typed(dumped) == to_serialize

    for value in to_serialize.values():
        assert serde.loads_typed(serde.dumps_typed(value)) == value

def test_with_standard_serializer() -> None:
    """Verify that default JsonPlusSerializer fails with namespace crewmaster.*"""
    user_message = UserMessage(
        content="mensaje de prueba",
        timestamp=datetime.now().isoformat()
    )
    to_serialize = { "message": user_message }
    # Using the default serializer
    serde = JsonPlusSerializer()

    dumped = serde.dumps(to_serialize)
    with pytest.raises(ValueError) as exc_info:
        serde.loads(dumped)
    error_message = str(exc_info.value)
    assert "Invalid namespace" in error_message
    assert "crewmaster" in error_message

    