"""Enums."""

from enum import StrEnum


class LLMProvidersEnum(StrEnum):
    """Enum for different Large Language Models (LLMs)."""

    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"


class SummarisationModesEnum(StrEnum):
    """Enum for different summarization modes.

    Attributes:
        COMPACT: Simple summarisation using the `COMPACT` response mode in LlamaIndex.
        REFINE: Refined summarisation by iteratively refining the summary with each chunk of text
        that fed to the LLM directly.

    """

    COMPACT = "compact"
    REFINED = "refined"
