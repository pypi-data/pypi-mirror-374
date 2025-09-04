"""Veris AI Python SDK."""

from typing import Any

__version__ = "0.1.0"

# Import lightweight modules that only use base dependencies
from .jaeger_interface import JaegerClient
from .models import ResponseExpectation
from .observability import init_observability, instrument_fastapi_app
from .tool_mock import veris

# Lazy import for modules with heavy dependencies
_veris_runner = None
_VerisConfig = None


def veris_runner(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
    """Lazy loader for the veris_runner function from agents_wrapper.

    This function wraps OpenAI agents Runner.run to intercept tool calls
    through the Veris SDK's mocking infrastructure.

    This function requires the 'agents' extra dependencies:
    pip install veris-ai[agents]
    """
    global _veris_runner  # noqa: PLW0603
    if _veris_runner is None:
        try:
            from .agents_wrapper import veris_runner as _veris_runner_impl  # noqa: PLC0415

            _veris_runner = _veris_runner_impl
        except ImportError as e:
            error_msg = (
                "The 'veris_runner' function requires additional dependencies. "
                "Please install them with: pip install veris-ai[agents]"
            )
            raise ImportError(error_msg) from e
    return _veris_runner(*args, **kwargs)


def __getattr__(name: str) -> Any:  # noqa: ANN401
    """Lazy load VerisConfig class."""
    global _VerisConfig  # noqa: PLW0603
    if name == "VerisConfig":
        if _VerisConfig is None:
            try:
                from .agents_wrapper import VerisConfig as _VerisConfig_impl  # noqa: PLC0415

                _VerisConfig = _VerisConfig_impl
            except ImportError as e:
                error_msg = (
                    "The 'VerisConfig' class requires additional dependencies. "
                    "Please install them with: pip install veris-ai[agents]"
                )
                raise ImportError(error_msg) from e
        return _VerisConfig
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)


__all__ = [
    "veris",
    "JaegerClient",
    "ResponseExpectation",
    "init_observability",
    "instrument_fastapi_app",
    "veris_runner",
    "VerisConfig",
]
