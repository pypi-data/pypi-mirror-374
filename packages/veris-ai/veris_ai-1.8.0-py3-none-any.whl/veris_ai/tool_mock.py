import inspect
import json
import logging
from collections.abc import Callable
from contextlib import suppress
from contextvars import ContextVar
from functools import wraps
from typing import (
    Any,
    Literal,
    TypeVar,
    get_type_hints,
)

from veris_ai.logging import (
    log_tool_call_async,
    log_tool_call_sync,
    log_tool_response_async,
    log_tool_response_sync,
)
from veris_ai.models import ResponseExpectation
from veris_ai.api_client import get_api_client
from veris_ai.utils import convert_to_type, extract_json_schema, get_function_parameters

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Context variable to store session_id for each call
_session_id_context: ContextVar[str | None] = ContextVar("veris_session_id", default=None)


class VerisSDK:
    """Class for mocking tool calls."""

    def __init__(self) -> None:
        """Initialize the ToolMock class."""
        self._mcp = None

    @property
    def session_id(self) -> str | None:
        """Get the session_id from context variable."""
        return _session_id_context.get()

    def set_session_id(self, session_id: str) -> None:
        """Set the session_id in context variable."""
        _session_id_context.set(session_id)
        logger.info(f"Session ID set to {session_id}")

    def clear_session_id(self) -> None:
        """Clear the session_id from context variable."""
        _session_id_context.set(None)
        logger.info("Session ID cleared")

    @property
    def fastapi_mcp(self) -> Any | None:  # noqa: ANN401
        """Get the FastAPI MCP server."""
        return self._mcp

    def set_fastapi_mcp(self, **params_dict: Any) -> None:  # noqa: ANN401
        """Set the FastAPI MCP server with HTTP transport."""
        from fastapi import Depends, Request  # noqa: PLC0415
        from fastapi.security import OAuth2PasswordBearer  # noqa: PLC0415
        from fastapi_mcp import (  # type: ignore[import-untyped] # noqa: PLC0415
            AuthConfig,
            FastApiMCP,
        )

        oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

        async def authenticate_request(
            _: Request,
            token: str = Depends(oauth2_scheme),  # noqa: ARG001
        ) -> None:
            self.set_session_id(token)

        # Create auth config with dependencies
        auth_config = AuthConfig(
            dependencies=[Depends(authenticate_request)],
        )

        # Merge the provided params with our auth config
        if "auth_config" in params_dict:
            # Merge the provided auth config with our dependencies
            provided_auth_config = params_dict.pop("auth_config")
            if provided_auth_config.dependencies:
                auth_config.dependencies.extend(provided_auth_config.dependencies)
            # Copy other auth config properties if they exist
            for field, value in provided_auth_config.model_dump(exclude_none=True).items():
                if field != "dependencies" and hasattr(auth_config, field):
                    setattr(auth_config, field, value)

        # Create the FastApiMCP instance with merged parameters
        self._mcp = FastApiMCP(
            auth_config=auth_config,
            **params_dict,
        )

    def mock(  # noqa: C901, PLR0915
        self,
        mode: Literal["tool", "function", "spy"] = "tool",
        expects_response: bool | None = None,
        cache_response: bool | None = None,
    ) -> Callable:
        """Decorator for mocking tool calls."""

        def decorator(func: Callable) -> Callable:  # noqa: C901, PLR0915
            """Decorator for mocking tool calls."""
            # Check if the original function is async
            is_async = inspect.iscoroutinefunction(func)

            def create_mock_payload(
                *args: tuple[object, ...],
                **kwargs: Any,  # noqa: ANN401
            ) -> tuple[dict[str, Any], Any]:
                """Create the mock payload - shared logic for both sync and async."""
                type_hints = get_type_hints(func)

                # Extract return type object (not just the name)
                return_type_obj = type_hints.pop("return", Any)
                # Create parameter info
                parameters = get_function_parameters(func, args, kwargs)
                # Get function docstring
                docstring = inspect.getdoc(func) or ""
                nonlocal expects_response
                if expects_response is None and mode == "function":
                    expects_response = False
                # Prepare payload
                # Convert expects_response to response_expectation enum
                if expects_response is False:
                    response_expectation = ResponseExpectation.NONE
                elif expects_response is True:
                    response_expectation = ResponseExpectation.REQUIRED
                else:
                    response_expectation = ResponseExpectation.AUTO

                payload = {
                    "session_id": self.session_id,
                    "response_expectation": response_expectation.value,
                    "cache_response": bool(cache_response) if cache_response is not None else False,
                    "tool_call": {
                        "function_name": func.__name__,
                        "parameters": parameters,
                        "return_type": json.dumps(extract_json_schema(return_type_obj)),
                        "docstring": docstring,
                    },
                }

                return payload, return_type_obj

            @wraps(func)
            async def async_wrapper(
                *args: tuple[object, ...],
                **kwargs: Any,  # noqa: ANN401
            ) -> object:
                # Check if we're in simulation mode
                if not self.session_id:
                    # If not in simulation mode, execute the original function
                    return await func(*args, **kwargs)

                async def _execute_mock_logic(session_id: str) -> object:
                    # Handle spy mode - execute original function and log
                    if mode == "spy":
                        logger.info(f"Spying on function: {func.__name__}")

                        # Log the tool call
                        parameters = get_function_parameters(func, args, kwargs)

                        await log_tool_call_async(
                            session_id=session_id,
                            function_name=func.__name__,
                            parameters=parameters,
                            docstring=inspect.getdoc(func) or "",
                        )

                        # Execute the original function
                        result = await func(*args, **kwargs)

                        # Log the response
                        await log_tool_response_async(session_id=session_id, response=result)

                        return result

                    # Regular mock mode
                    api_client = get_api_client()
                    endpoint = api_client.tool_mock_endpoint

                    logger.info(f"Simulating function: {func.__name__}")
                    payload, return_type_obj = create_mock_payload(*args, **kwargs)

                    # Send request to endpoint
                    mock_result = await api_client.post_async(endpoint, payload)
                    logger.info(f"Mock response: {mock_result}")

                    if isinstance(mock_result, str):
                        with suppress(json.JSONDecodeError):
                            mock_result = json.loads(mock_result)
                            return convert_to_type(mock_result, return_type_obj)
                    return convert_to_type(mock_result, return_type_obj)

                # Create a top-level span for the simulated mock call if OpenTelemetry is available
                try:
                    from opentelemetry import trace  # type: ignore[import-not-found]

                    tracer = trace.get_tracer("veris_ai.tool_mock")
                    span_name = f"mock.{func.__name__}"
                    with tracer.start_as_current_span(span_name) as span:  # type: ignore[attr-defined]
                        span.set_attribute("veris_ai.session.id", self.session_id or "")  # type: ignore[attr-defined]
                        span.set_attribute("veris_ai.mock.mode", mode)  # type: ignore[attr-defined]
                        return await _execute_mock_logic(self.session_id)
                except Exception:
                    # If OpenTelemetry is not available, run without span
                    return await _execute_mock_logic(self.session_id)

            @wraps(func)
            def sync_wrapper(
                *args: tuple[object, ...],
                **kwargs: Any,  # noqa: ANN401
            ) -> object:
                # Check if we're in simulation mode
                if not self.session_id:
                    # If not in simulation mode, execute the original function
                    return func(*args, **kwargs)

                def _execute_mock_logic(session_id: str) -> object:
                    # Handle spy mode - execute original function and log
                    if mode == "spy":
                        logger.info(f"Spying on function: {func.__name__}")

                        # Log the tool call
                        parameters = get_function_parameters(func, args, kwargs)

                        log_tool_call_sync(
                            session_id=session_id,
                            function_name=func.__name__,
                            parameters=parameters,
                            docstring=inspect.getdoc(func) or "",
                        )

                        # Execute the original function
                        result = func(*args, **kwargs)

                        # Log the response
                        log_tool_response_sync(session_id=session_id, response=result)

                        return result

                    # Regular mock mode
                    api_client = get_api_client()
                    endpoint = api_client.tool_mock_endpoint

                    logger.info(f"Simulating function: {func.__name__}")
                    payload, return_type_obj = create_mock_payload(*args, **kwargs)

                    # Send request to endpoint
                    mock_result = api_client.post_sync(endpoint, payload)
                    logger.info(f"Mock response: {mock_result}")

                    if isinstance(mock_result, str):
                        with suppress(json.JSONDecodeError):
                            mock_result = json.loads(mock_result)
                            return convert_to_type(mock_result, return_type_obj)
                    return convert_to_type(mock_result, return_type_obj)

                # Create a top-level span for the simulated mock call if OpenTelemetry is available
                try:
                    from opentelemetry import trace  # type: ignore[import-not-found]

                    tracer = trace.get_tracer("veris_ai.tool_mock")
                    span_name = f"mock.{func.__name__}"
                    with tracer.start_as_current_span(span_name) as span:  # type: ignore[attr-defined]
                        span.set_attribute("veris_ai.session.id", self.session_id or "")  # type: ignore[attr-defined]
                        span.set_attribute("veris_ai.mock.mode", mode)  # type: ignore[attr-defined]
                        return _execute_mock_logic(self.session_id)
                except Exception:
                    # If OpenTelemetry is not available, run without span
                    return _execute_mock_logic(self.session_id)

            # Return the appropriate wrapper based on whether the function is async
            return async_wrapper if is_async else sync_wrapper

        return decorator

    def stub(self, return_value: Any) -> Callable:  # noqa: ANN401
        """Decorator for stubbing toolw calls."""

        def decorator(func: Callable) -> Callable:
            # Check if the original function is async
            is_async = inspect.iscoroutinefunction(func)

            @wraps(func)
            async def async_wrapper(
                *args: tuple[object, ...],
                **kwargs: Any,  # noqa: ANN401
            ) -> object:
                if not self.session_id:
                    # If not in simulation mode, execute the original function
                    return await func(*args, **kwargs)
                logger.info(f"Stubbing function: {func.__name__}")
                return return_value

            @wraps(func)
            def sync_wrapper(*args: tuple[object, ...], **kwargs: Any) -> object:  # noqa: ANN401
                if not self.session_id:
                    # If not in simulation mode, execute the original function
                    return func(*args, **kwargs)
                logger.info(f"Stubbing function: {func.__name__}")
                return return_value

            # Return the appropriate wrapper based on whether the function is async
            return async_wrapper if is_async else sync_wrapper

        return decorator


veris = VerisSDK()
