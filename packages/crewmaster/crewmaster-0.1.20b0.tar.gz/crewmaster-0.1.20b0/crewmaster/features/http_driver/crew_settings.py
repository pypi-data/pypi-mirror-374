from pydantic import (
    Field,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class CrewSettings(BaseSettings):
    """
    Clase de Pydantinc para manejar los settings

    Ver: https://fastapi.tiangolo.com/advanced/settings/
    """
    # api key para Open AI
    llm_api_key_open_ai: str = Field(min_length=10)
    llm_model_open_ai: str = Field(min_length=10)
    llm_temperature_open_ai: int = 0

    model_config = SettingsConfigDict(
        extra="allow",
        env_file=""
    )
