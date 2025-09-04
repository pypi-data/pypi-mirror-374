"""Logging utilities for VERIS tool calls and responses."""

import json
import logging
from typing import Any

from veris_ai.api_client import get_api_client

logger = logging.getLogger(__name__)


def log_tool_call(
    session_id: str,
    function_name: str,
    parameters: str,
    docstring: str,
) -> None:
    """Log tool call synchronously to the VERIS logging endpoint."""
    api_client = get_api_client()
    endpoint = api_client.get_log_tool_call_endpoint(session_id)
    payload = {
        "function_name": function_name,
        "parameters": json.loads(parameters),
        "docstring": docstring,
    }
    try:
        api_client.post(endpoint, payload)
        logger.debug(f"Tool call logged for {function_name}")
    except Exception as e:
        logger.warning(f"Failed to log tool call for {function_name}: {e}")


def log_tool_response(session_id: str, response: Any) -> None:  # noqa: ANN401
    """Log tool response synchronously to the VERIS logging endpoint."""
    api_client = get_api_client()
    endpoint = api_client.get_log_tool_response_endpoint(session_id)

    payload = {
        "response": json.dumps(response, default=str),
    }

    try:
        api_client.post(endpoint, payload)
        logger.debug("Tool response logged")
    except Exception as e:
        logger.warning(f"Failed to log tool response: {e}")
