"""Centralized API client for VERIS simulation endpoints."""

import logging
import os
from typing import Any

import httpx
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class SimulatorAPIClient:
    """Centralized client for making requests to VERIS simulation endpoints."""

    def __init__(self) -> None:
        """Initialize the API client with configuration from environment variables."""
        self.base_url = os.getenv("VERIS_API_URL", "https://simulation.api.veris.ai/")
        self.api_key = os.getenv("VERIS_API_KEY")
        self.timeout = float(os.getenv("VERIS_MOCK_TIMEOUT", "90.0"))

    def _build_headers(self) -> dict[str, str] | None:
        """Build headers including OpenTelemetry tracing and API key."""
        headers: dict[str, str] | None = None
        # Add API key header if available
        if self.api_key:
            if headers is None:
                headers = {}
            headers["x-api-key"] = self.api_key

        return headers

    def post(self, endpoint: str, payload: dict[str, Any]) -> Any:  # noqa: ANN401
        """Make a synchronous POST request to the specified endpoint."""
        headers = self._build_headers()
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            return response.json() if response.content else None

    @property
    def tool_mock_endpoint(self) -> str:
        """Get the tool mock endpoint URL."""
        return urljoin(self.base_url, "v2/tool_mock")

    def get_log_tool_call_endpoint(self, session_id: str) -> str:
        """Get the log tool call endpoint URL."""
        return urljoin(self.base_url, f"v2/simulations/{session_id}/log_tool_call")

    def get_log_tool_response_endpoint(self, session_id: str) -> str:
        """Get the log tool response endpoint URL."""
        return urljoin(self.base_url, f"v2/simulations/{session_id}/log_tool_response")


# Global singleton instance
_api_client = SimulatorAPIClient()


def get_api_client() -> SimulatorAPIClient:
    """Get the global API client instance."""
    return _api_client
