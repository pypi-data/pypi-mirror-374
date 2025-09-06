from langgraph.checkpoint.memory import (
    MemorySaver,
    BaseCheckpointSaver,
)
from ...helpers.json_serializar_from_custom_models import (
    JsonSerializarFromCustomModels
)


def memory_factory() -> BaseCheckpointSaver:
    serde = JsonSerializarFromCustomModels()
    checkpointer = MemorySaver(
        serde=serde
    )
    return checkpointer
