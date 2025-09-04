"""Simplified tests for the OpenAI agents wrapper with live API calls only."""

import json
import os
import sys
import pytest
from typing import Any
from unittest.mock import AsyncMock, patch, MagicMock

# Workaround for Python 3.13 httpx compatibility issue
if sys.version_info >= (3, 13):
    import httpx

    # Pre-import httpx to ensure it's available for isinstance checks
    _ = httpx.AsyncClient

from agents import Agent, FunctionTool

from veris_ai import veris, veris_runner, VerisConfig

# Skip tests if no API key is available
if not os.environ.get("OPENAI_API_KEY"):
    pytest.skip(
        "OPENAI_API_KEY not set - skipping tests that require real API", allow_module_level=True
    )


# Simple tool implementations
async def add_numbers_impl(context: Any, arguments: str) -> str:
    """Add two numbers together."""
    args = json.loads(arguments)
    result = args.get("a", 0) + args.get("b", 0)
    return json.dumps({"result": result})


async def multiply_numbers_impl(context: Any, arguments: str) -> str:
    """Multiply two numbers together."""
    args = json.loads(arguments)
    result = args.get("a", 0) * args.get("b", 0)
    return json.dumps({"result": result})


@pytest.fixture
def test_agent():
    """Fixture that creates a simple test agent with math tools."""
    add_tool = FunctionTool(
        name="add_numbers",
        description="Add two numbers together",
        params_json_schema={
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"},
            },
            "required": ["a", "b"],
            "additionalProperties": False,
        },
        on_invoke_tool=add_numbers_impl,
    )

    multiply_tool = FunctionTool(
        name="multiply_numbers",
        description="Multiply two numbers",
        params_json_schema={
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"},
            },
            "required": ["a", "b"],
            "additionalProperties": False,
        },
        on_invoke_tool=multiply_numbers_impl,
    )

    return Agent(
        name="MathAssistant",
        model="gpt-4o-mini",  # Using cheaper model for testing
        instructions="You are a helpful math assistant. Use the add_numbers or multiply_numbers tools to perform calculations when asked.",
        tools=[add_tool, multiply_tool],
    )


@pytest.mark.asyncio
async def test_veris_runner_basic(test_agent):
    """Test basic veris_runner functionality with real OpenAI API."""
    veris.clear_session_id()  # Ensure no session is set

    # Run a simple calculation
    result = await veris_runner(test_agent, "What is 5 plus 3?", max_turns=2)

    # Verify we got a result
    assert result is not None
    # Check that the agent used the tool and got the correct answer (8)
    last_message = result.to_input_list()[-1]
    if isinstance(last_message, dict) and "content" in last_message:
        # Handle different message formats
        content = last_message["content"]
        if isinstance(content, list) and len(content) > 0:
            # New format with list of content items
            text = content[0].get("text", "")
        else:
            # String content
            text = str(content)
    else:
        text = str(last_message)
    assert "8" in text


@pytest.mark.asyncio
async def test_veris_runner_with_multiplication(test_agent):
    """Test veris_runner with multiplication tool."""
    veris.clear_session_id()

    # Run a multiplication
    result = await veris_runner(test_agent, "What is 6 times 7?", max_turns=2)

    # Verify we got a result
    assert result is not None
    # Check that the agent got the correct answer (42)
    last_message = result.to_input_list()[-1]
    if isinstance(last_message, dict) and "content" in last_message:
        content = last_message["content"]
        if isinstance(content, list) and len(content) > 0:
            text = content[0].get("text", "")
        else:
            text = str(content)
    else:
        text = str(last_message)
    assert "42" in text


@pytest.mark.asyncio
async def test_veris_runner_with_config(test_agent):
    """Test veris_runner with VerisConfig (no actual mocking, just config validation)."""
    veris.clear_session_id()

    # Create config that would only intercept add_numbers (if session was set)
    config = VerisConfig(include_tools=["add_numbers"])

    # Run with config
    result = await veris_runner(test_agent, "Calculate 2 plus 2", veris_config=config, max_turns=2)

    # Verify we got a result
    assert result is not None
    # Check that the calculation was performed
    last_message = result.to_input_list()[-1]
    if isinstance(last_message, dict) and "content" in last_message:
        content = last_message["content"]
        if isinstance(content, list) and len(content) > 0:
            text = content[0].get("text", "")
        else:
            text = str(content)
    else:
        text = str(last_message)
    assert "4" in text


@pytest.mark.asyncio
async def test_veris_runner_preserves_kwargs(test_agent):
    """Test that veris_runner properly passes through kwargs."""
    veris.clear_session_id()

    # Call with custom kwargs
    result = await veris_runner(
        test_agent,
        "Just say hello, don't calculate anything",
        max_turns=1,
        context={"test": "context"},
    )

    # Verify we got a result
    assert result is not None
    # The agent should have responded without using tools
    messages = result.to_input_list()
    assert len(messages) > 0


def test_veris_config_validation():
    """Test that VerisConfig validates correctly."""
    # VerisConfig should allow both include_tools and exclude_tools to be set
    # The validation happens in veris_runner, not in VerisConfig itself

    # Test that include_tools alone works
    config = VerisConfig(include_tools=["tool1", "tool2"])
    assert config.include_tools == ["tool1", "tool2"]

    # Test that exclude_tools alone works
    config = VerisConfig(exclude_tools=["tool3"])
    assert config.exclude_tools == ["tool3"]

    # Test that both can be set (validation happens in veris_runner)
    config = VerisConfig(include_tools=["tool1"], exclude_tools=["tool2"])
    assert config.include_tools == ["tool1"]
    assert config.exclude_tools == ["tool2"]

    # Test that empty config works
    config = VerisConfig()
    assert config.include_tools is None
    assert config.exclude_tools is None


@pytest.fixture
def mock_veris_endpoint():
    """Fixture that mocks the veris SDK's HTTP request method."""
    calls = []

    def mock_request(endpoint, payload):
        """Mock the post_sync method."""
        # Record the call
        calls.append({"endpoint": endpoint, "payload": payload})

        # Return a distinctive mocked value
        return {"result": 999}

    # Patch the post_sync method of the API client
    from veris_ai.api_client import get_api_client

    with patch.object(get_api_client(), "post_sync", side_effect=mock_request):
        yield {"calls": calls}


@pytest.fixture
def simulation_env_with_session():
    """Fixture that sets up simulation environment variables and session ID."""
    # Store original values
    original_endpoint = os.environ.get("VERIS_ENDPOINT_URL")

    # Set up simulation environment
    os.environ["VERIS_ENDPOINT_URL"] = "http://localhost:8000"

    # Set session ID
    veris.set_session_id("test-session-123")

    yield

    # Clean up
    veris.clear_session_id()

    # Restore original environment variables
    if original_endpoint is None:
        os.environ.pop("VERIS_ENDPOINT_URL", None)
    else:
        os.environ["VERIS_ENDPOINT_URL"] = original_endpoint


@pytest.mark.asyncio
async def test_veris_runner_with_session_calls_endpoint(
    mock_veris_endpoint, simulation_env_with_session, test_agent
):
    """Test that veris_runner calls the veris endpoint when session is set."""

    # Run with the mocked endpoint (increase max_turns since mocking may need more turns)
    result = await veris_runner(test_agent, "What is 10 plus 5?", max_turns=5)

    # Verify the endpoint was called
    assert len(mock_veris_endpoint["calls"]) > 0, "Veris endpoint should have been called"

    # Verify the call had correct structure
    first_call = mock_veris_endpoint["calls"][0]
    assert first_call["endpoint"] == "http://localhost:8000/api/v2/tool_mock"
    assert first_call["payload"]["session_id"] == "test-session-123"
    # Check that the call contains tool information
    # The payload structure depends on how the wrapper builds it
    assert "add_numbers" in str(first_call["payload"]) or "veris_tool_function" in str(
        first_call["payload"]
    )

    # We've verified the endpoint was called with the correct parameters
    # The agent's response handling is a separate concern
    assert result is not None


@pytest.mark.asyncio
async def test_veris_runner_without_session_does_not_call_endpoint(mock_veris_endpoint, test_agent):
    """Test that veris_runner does NOT call the endpoint when no session is set."""
    # Ensure we're NOT in simulation mode and no session is set
    os.environ.pop("ENV", None)
    veris.clear_session_id()

    # Run without session - should use real tools
    result = await veris_runner(test_agent, "What is 3 plus 4?", max_turns=2)

    # Verify the endpoint was NOT called
    assert len(mock_veris_endpoint["calls"]) == 0, (
        "Veris endpoint should not be called without session"
    )

    # Verify real calculation was performed (7, not 999)
    assert result is not None
    last_message = result.to_input_list()[-1]
    if isinstance(last_message, dict) and "content" in last_message:
        content = last_message["content"]
        if isinstance(content, list) and len(content) > 0:
            text = content[0].get("text", "")
        else:
            text = str(content)
    else:
        text = str(last_message)
    assert "7" in text, "Should use real calculation"
    assert "999" not in text, "Should not use mocked result"
