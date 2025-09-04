"""Example of using the Veris SDK with OpenAI agents to intercept tool calls."""

import asyncio
import os
import sys

from veris_ai import veris, wrap

# Ensure the openai-agents package is installed
try:
    from agents import Agent, Runner, function_tool
except ImportError:
    print("Please install the openai-agents package: pip install veris-ai[agents]")
    sys.exit(1)


# Define some example tools
@function_tool
def calculator(x: int, y: int, operation: str = "add") -> int:
    """Performs arithmetic operations on two numbers."""
    if operation == "add":
        return x + y
    if operation == "multiply":
        return x * y
    if operation == "subtract":
        return x - y
    if operation == "divide":
        return x // y if y != 0 else 0
    return 0


@function_tool
def search_web(query: str) -> str:
    """Searches the web for information."""
    return f"Search results for: {query}"


@function_tool
def get_weather(location: str) -> str:
    """Gets current weather for a location."""
    return f"Weather in {location}: Sunny, 72°F"


async def example_basic_wrap() -> None:
    """Basic example: Wrap all tools."""
    print("\n" + "=" * 60)
    print("Example 1: Basic Wrap - All Tools Intercepted")
    print("=" * 60)

    # Create an agent with tools
    agent = Agent(
        name="Assistant",
        model="gpt-4",
        tools=[calculator, search_web, get_weather],
        instructions="You are a helpful assistant with various tools.",
    )

    # Wrap the Runner.run method - all tools will be intercepted
    wrapped_run = wrap(Runner.run)

    # Use it like normal Runner.run
    result = await wrapped_run(agent, "What's 10 + 5? Also search for Python tutorials.")
    print(f"Result: {result.output}")


async def example_selective_wrap() -> None:
    """Example with selective tool interception."""
    print("\n" + "=" * 60)
    print("Example 2: Selective Wrap - Only Specific Tools")
    print("=" * 60)

    agent = Agent(
        name="Assistant",
        model="gpt-4",
        tools=[calculator, search_web, get_weather],
        instructions="You are a helpful assistant.",
    )

    # Only intercept calculator and search_web
    wrapped_run = wrap(Runner.run, include_tools=["calculator", "search_web"])

    print("📝 Only 'calculator' and 'search_web' will be mocked via Veris")
    print("   'get_weather' will run normally")

    result = await wrapped_run(agent, "Calculate 5+3 and check weather in NYC")
    print(f"Result: {result.output}")


async def example_exclude_tools() -> None:
    """Example excluding specific tools from interception."""
    print("\n" + "=" * 60)
    print("Example 3: Exclude Tools - Keep Some Tools Normal")
    print("=" * 60)

    agent = Agent(
        name="Assistant",
        model="gpt-4",
        tools=[calculator, search_web, get_weather],
        instructions="You are a helpful assistant.",
    )

    # Intercept everything EXCEPT get_weather
    wrapped_run = wrap(Runner.run, exclude_tools=["get_weather"])

    print("📝 All tools EXCEPT 'get_weather' will be mocked via Veris")

    result = await wrapped_run(agent, "Calculate 10*5 and check weather in London")
    print(f"Result: {result.output}")


async def example_coroutine_wrap() -> None:
    """Example wrapping a coroutine directly."""
    print("\n" + "=" * 60)
    print("Example 4: Direct Coroutine Wrap")
    print("=" * 60)

    agent = Agent(
        name="Assistant",
        model="gpt-4",
        tools=[calculator],
        instructions="You are a helpful assistant.",
    )

    # Wrap the coroutine directly
    result = await wrap(Runner.run(agent, "What's 7 * 8?"))
    print(f"Result: {result.output}")


async def main() -> None:
    """Run all examples."""
    print("\n🚀 VERIS SDK - OPENAI AGENTS WRAPPER EXAMPLES")
    print("\nThese examples demonstrate different ways to intercept tool calls")
    print("from OpenAI agents and route them through the Veris SDK.\n")

    # Set up the environment
    # In production, these would be set as environment variables
    if not os.getenv("VERIS_ENDPOINT_URL"):
        print("⚠️  VERIS_ENDPOINT_URL not set. Using demo endpoint.")
        os.environ["VERIS_ENDPOINT_URL"] = "http://demo.veris.ai"

    # Set a session ID to enable mocking
    veris.set_session_id("example-session-123")
    print(f"✅ Session ID set: {veris.session_id}")

    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  Note: OPENAI_API_KEY not set.")
        print("   The examples will show the pattern but won't actually run.")
        print("   Set your API key to see real agent execution.\n")

    try:
        # Run examples
        await example_basic_wrap()
        await example_selective_wrap()
        await example_exclude_tools()
        await example_coroutine_wrap()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure to:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Set VERIS_ENDPOINT_URL to your Veris endpoint")
        print("3. Install dependencies: pip install veris-ai[agents]")
    finally:
        # Clear session when done
        veris.clear_session_id()
        print("\n✅ Session cleared")

    print("\n✨ Examples complete!")
    print("\nNext steps:")
    print("1. Set up your Veris endpoint")
    print("2. Configure your OpenAI API key")
    print("3. Use wrap() to intercept tool calls in your agents")


if __name__ == "__main__":
    asyncio.run(main())
