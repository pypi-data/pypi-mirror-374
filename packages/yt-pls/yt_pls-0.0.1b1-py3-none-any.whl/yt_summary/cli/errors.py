"""Custom argparse type for LLMProvidersEnum validation."""

import argparse
from enum import StrEnum

from yt_summary.schemas.enums import LLMProvidersEnum, SummarisationModesEnum


def check_type(value: str, enum: type[StrEnum]) -> None:
    """Ensure the argument is a valid enum value.

    Args:
        value: The string to validate.
        enum: The enum type to validate against.

    Raises:
        argparse.ArgumentTypeError: If the value is not valid.

    """
    if value not in [e.value for e in enum]:
        raise argparse.ArgumentTypeError(f"Invalid value '{value}'. Must be one of: {[e.value for e in enum]}")


def check_provider_type(provider: str) -> None:
    """Ensure the provider argument is a valid LLMProvidersEnum value.

    Args:
        provider (str): The provider string to validate.

    Raises:
        argparse.ArgumentTypeError: If the provider is not valid.

    """
    return check_type(provider, LLMProvidersEnum)


def check_mode_type(mode: str) -> None:
    """Ensure the mode argument is a valid SummarisationModesEnum value.

    Args:
        mode (str): The mode string to validate.

    Raises:
        argparse.ArgumentTypeError: If the mode is not valid.

    """
    return check_type(mode, SummarisationModesEnum)
