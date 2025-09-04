"""OpenAI Agents wrapper for automatic tool mocking via Veris SDK."""

import asyncio
import inspect
import json
import logging
from collections.abc import Callable
from typing import Any

from agents import RunResult, Runner
from pydantic import BaseModel

from veris_ai import veris

logger = logging.getLogger(__name__)


def _wrap(
    include_tools: list[str] | None = None,
    exclude_tools: list[str] | None = None,
) -> Callable:
    """Private wrapper for OpenAI agents Runner to intercept tool calls through Veris SDK.

    This function transparently intercepts tool calls from OpenAI agents and
    routes them through the Veris SDK's mocking infrastructure.

    Args:
        include_tools: Optional list of tool names to intercept (only these if provided)
        exclude_tools: Optional list of tool names to NOT intercept (these run normally)

    Returns:
        A wrapped Runner.run function

    Raises:
        ValueError: If both include_tools and exclude_tools are specified
        ImportError: If agents package is not installed
    """
    if include_tools and exclude_tools:
        msg = "Cannot specify both include_tools and exclude_tools"
        raise ValueError(msg)

    def wrapped_run_func(run_func: Callable) -> Callable:
        """Inner wrapper that takes the actual Runner.run function."""
        try:
            from agents import FunctionTool  # type: ignore[import-untyped] # noqa: PLC0415
        except ImportError as e:
            msg = "openai-agents package not installed. Install with: pip install veris-ai[agents]"
            raise ImportError(msg) from e

        async def wrapped_run(starting_agent: Any, input_text: str, **kwargs: Any) -> Any:  # noqa: ANN401
            """Wrapped version of Runner.run that intercepts tool calls."""
            # Patch all tools in the agent
            original_tools = []

            if hasattr(starting_agent, "tools") and starting_agent.tools:
                for tool in starting_agent.tools:
                    if isinstance(tool, FunctionTool):
                        tool_name = getattr(tool, "name", None)

                        # Check if we should patch this tool
                        if tool_name and _should_intercept_tool(
                            tool_name, include_tools, exclude_tools
                        ):
                            # Save the original invoke function
                            original_tools.append((tool, tool.on_invoke_tool))  # type: ignore[attr-defined]

                            # Create veris-wrapped version
                            tool.on_invoke_tool = _create_veris_wrapped_invoke(  # type: ignore[attr-defined]
                                tool,
                                tool.on_invoke_tool,  # type: ignore[attr-defined]
                            )

            try:
                # Call the original Runner.run with the patched agent
                return await run_func(starting_agent, input_text, **kwargs)
            finally:
                # Restore all original tool functions
                for tool, original_invoke in original_tools:
                    tool.on_invoke_tool = original_invoke  # type: ignore[attr-defined]

        # Preserve function metadata
        wrapped_run.__name__ = getattr(run_func, "__name__", "wrapped_run")
        wrapped_run.__doc__ = getattr(run_func, "__doc__", "Wrapped Runner.run function")

        # Also provide a sync version
        def wrapped_run_sync(starting_agent: Any, input_text: str, **kwargs: Any) -> Any:  # noqa: ANN401
            """Sync version of wrapped Runner.run."""
            return asyncio.run(wrapped_run(starting_agent, input_text, **kwargs))

        # Add sync version as an attribute
        wrapped_run.run_sync = wrapped_run_sync  # type: ignore[attr-defined]

        return wrapped_run

    return wrapped_run_func


def _should_intercept_tool(
    tool_name: str,
    include_tools: list[str] | None,
    exclude_tools: list[str] | None,
) -> bool:
    """Determine if a tool should be intercepted based on include/exclude lists.

    Args:
        tool_name: Name of the tool
        include_tools: If provided, only these tools are intercepted
        exclude_tools: If provided, these tools are NOT intercepted

    Returns:
        True if the tool should be intercepted, False otherwise
    """
    if include_tools:
        return tool_name in include_tools
    if exclude_tools:
        return tool_name not in exclude_tools
    return True


def _create_veris_wrapped_invoke(  # noqa: C901
    tool: Any,  # noqa: ANN401
    original_invoke: Callable,
) -> Callable:
    """Create a wrapped invoke function that uses veris.mock().

    Args:
        tool: The FunctionTool instance
        original_invoke: The original on_invoke_tool function

    Returns:
        A wrapped invoke function that routes through Veris SDK
    """
    # Extract tool metadata
    tool_name = tool.name
    tool_schema = tool.params_json_schema if hasattr(tool, "params_json_schema") else {}

    # Create a function that will be decorated with veris.mock()
    @veris.mock(mode="tool")
    async def veris_tool_function(**_kwargs: Any) -> Any:  # noqa: ANN401
        """Mock function for tool execution."""
        # This function's signature doesn't matter as veris.mock()
        # will intercept and send the metadata to the endpoint
        return f"Mock response for {tool_name}"

    async def wrapped_invoke(context: Any, arguments: str) -> Any:  # noqa: ANN401
        """Wrapped invoke function that routes through Veris SDK."""
        # Only intercept if we have a session ID
        if not veris.session_id:
            # No session, run original
            return await original_invoke(context, arguments)

        # Parse arguments
        try:
            args_dict = json.loads(arguments) if arguments else {}
        except json.JSONDecodeError:
            args_dict = {"raw_arguments": arguments}

        # Set up the function with proper metadata for veris.mock()
        veris_tool_function.__name__ = tool_name
        veris_tool_function.__doc__ = getattr(tool, "description", "")

        # Add type hints based on schema if available
        if tool_schema and "properties" in tool_schema:
            # Create a simple signature based on schema
            params = []
            for param_name, param_info in tool_schema["properties"].items():
                # Simplified type mapping
                param_type: type[Any] = Any
                if "type" in param_info:
                    type_map = {
                        "string": str,
                        "number": float,
                        "integer": int,
                        "boolean": bool,
                        "array": list,
                        "object": dict,
                    }
                    param_type = type_map.get(param_info["type"], Any)
                params.append(
                    inspect.Parameter(
                        param_name,
                        inspect.Parameter.KEYWORD_ONLY,
                        annotation=param_type,
                    )
                )

            if params:
                veris_tool_function.__signature__ = inspect.Signature(params)

        # Call the veris-wrapped function with the arguments
        try:
            return await veris_tool_function(**args_dict)
        except Exception as e:
            # If mocking fails, fall back to original
            logger.warning(f"Veris mock failed for {tool_name}, falling back to original: {e}")
            return await original_invoke(context, arguments)

    # Handle sync version if original is sync
    if not asyncio.iscoroutinefunction(original_invoke):

        def sync_wrapped_invoke(context: Any, arguments: str) -> Any:  # noqa: ANN401
            """Sync version of wrapped invoke."""
            return asyncio.run(wrapped_invoke(context, arguments))

        return sync_wrapped_invoke

    return wrapped_invoke


class VerisConfig(BaseModel):
    """Configuration for the Veris SDK."""

    include_tools: list[str] | None = None
    exclude_tools: list[str] | None = None


def veris_runner(
    starting_agent: Any,  # noqa: ANN401
    input_text: str,
    veris_config: VerisConfig | None = None,
    **kwargs: Any,  # noqa: ANN401
) -> RunResult:  # noqa: ANN401
    """Veris-wrapped version of OpenAI agents Runner.run.

    This function wraps the OpenAI agents Runner.run to intercept tool calls
    and route them through the Veris SDK's mocking infrastructure. It can be
    used as a drop-in replacement for Runner.run with an additional veris_config parameter.

    Args:
        starting_agent: The OpenAI agent to run
        input_text: The input text to process
        veris_config: Optional configuration for Veris SDK tool interception
        **kwargs: Additional arguments to pass to Runner.run

    Returns:
        The result from Runner.run

    Example:
        ```python
        from veris_ai import veris_runner, VerisConfig
        from agents import Agent, FunctionTool

        # Define your agent with tools
        agent = Agent(...)

        # Use veris_runner instead of Runner.run
        result = await veris_runner(agent, "Process this input")

        # Or with specific tool configuration
        config = VerisConfig(include_tools=["calculator", "search"])
        result = await veris_runner(agent, "Calculate 2+2", veris_config=config)
        ```
    """

    # Extract config values
    include_tools = None
    exclude_tools = None
    if veris_config:
        include_tools = veris_config.include_tools
        exclude_tools = veris_config.exclude_tools

    # Create the wrapped version of Runner.run with the config
    wrapped_run = _wrap(include_tools=include_tools, exclude_tools=exclude_tools)(Runner.run)

    # Execute the wrapped run function
    return wrapped_run(starting_agent, input_text, **kwargs)
