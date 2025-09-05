"""Configuration for different language models."""

from pydantic import BaseModel

from yt_summary.config import settings
from yt_summary.schemas.enums import LLMProvidersEnum


class LLMConfigs(BaseModel):
    """Language model configurations.

    Attributes:
        key_env: Environment variable name for the API key.
        default_key: Default API key if environment variable is not set.
        default_model: Default model name to use.

    """

    key_name: str
    default_key: str
    default_model: str


class OPENAIConfig(LLMConfigs):
    """OpenAI model configuration."""

    key_name: str = "OPENAI_API_KEY"
    default_key: str = settings.OPENAI_API_KEY
    default_model: str = settings.OPENAI_MODEL


class GOOGLEConfig(LLMConfigs):
    """Google model configuration."""

    key_name: str = "GOOGLE_API_KEY"
    default_key: str = settings.GOOGLE_API_KEY
    default_model: str = settings.GOOGLE_MODEL


class ANTHROPICConfig(LLMConfigs):
    """Anthropic model configuration."""

    key_name: str = "ANTHROPIC_API_KEY"
    default_key: str = settings.ANTHROPIC_API_KEY
    default_model: str = settings.ANTHROPIC_MODEL


llm_configs: dict[LLMProvidersEnum, LLMConfigs] = {
    LLMProvidersEnum.OPENAI: OPENAIConfig(),
    LLMProvidersEnum.GOOGLE: GOOGLEConfig(),
    LLMProvidersEnum.ANTHROPIC: ANTHROPICConfig(),
}
