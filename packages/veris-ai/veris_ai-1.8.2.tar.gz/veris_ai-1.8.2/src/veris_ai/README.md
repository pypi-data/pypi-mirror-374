# Veris AI Module Architecture

This module contains the core implementation of the Veris AI Python SDK. Each component focuses on a specific aspect of tool mocking, tracing, and MCP integration.

## Quick Reference

**Purpose**: Core SDK implementation with modular architecture  
**Entry Point**: [`__init__.py`](__init__.py) handles lazy imports and public API exports  
**Source of Truth**: Individual module files contain implementation details

## Module Overview

**Semantic Tag**: `core-modules`

| Module | Purpose | Key Classes/Functions | Lines |
|--------|---------|----------------------|-------|
| [`tool_mock.py`](tool_mock.py) | Function mocking & FastAPI MCP | `VerisSDK`, `@mock`, `@stub` | 327 |
| [`utils.py`](utils.py) | Type utilities & JSON schema | `extract_json_schema()` | 272 |
| [`logging.py`](logging.py) | Logging configuration | `setup_logging()` | 116 |
| [`models.py`](models.py) | Data models | Type definitions | 12 |
| [`jaeger_interface/`](jaeger_interface/) | Jaeger Query API wrapper | `JaegerClient` | See module README |

## Core Workflows

**Semantic Tag**: `implementation-flows`

### Mock Flow
1. **Decoration**: `@veris.mock()` captures function metadata
2. **Environment Check**: `ENV=simulation` determines behavior  
3. **API Call**: POST to `{VERIS_ENDPOINT_URL}/api/v2/tool_mock`
4. **Type Conversion**: Response converted using `extract_json_schema()`

**Implementation**: [`tool_mock.py:200-250`](tool_mock.py)

### Spy Flow  
1. **Pre-execution Logging**: Call details sent to `/api/v2/log_tool_call`
2. **Function Execution**: Original function runs normally
3. **Post-execution Logging**: Response sent to `/api/v2/log_tool_response`

**Implementation**: [`tool_mock.py:250-300`](tool_mock.py)


## Configuration

**Semantic Tag**: `module-config`

Environment variables are processed in [`tool_mock.py`](tool_mock.py):

- `VERIS_ENDPOINT_URL`: Mock server endpoint
- `VERIS_MOCK_TIMEOUT`: Request timeout (default: 90s)  
- `ENV`: Set to `"simulation"` for mock mode

### Observability (OTLP / Logfire)

When using the observability helpers (`init_observability`, `instrument_fastapi_app`), configure the following environment variables so traces export correctly and are attributed to the right service name:

- `OTEL_SERVICE_NAME` — e.g. `simulation-server` (keep consistent with any `VERIS_SERVICE_NAME` you use)
- `OTEL_EXPORTER_OTLP_ENDPOINT` — e.g. `https://logfire-api.pydantic.dev`
- `LOGFIRE_TOKEN` — API token for Logfire
- `OTEL_EXPORTER_OTLP_HEADERS` — e.g. `Authorization=Bearer <LOGFIRE_TOKEN>` (quote the value)

Minimal shell setup:

```bash
export OTEL_SERVICE_NAME="simulation-server"
export OTEL_EXPORTER_OTLP_ENDPOINT="https://logfire-api.pydantic.dev"
export LOGFIRE_TOKEN="<your-token>"
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=${LOGFIRE_TOKEN}"
```

Then in code:

```python
from veris_ai import init_observability, instrument_fastapi_app
init_observability()
app = FastAPI()
instrument_fastapi_app(app)
```

## Development Notes

**Semantic Tag**: `development-patterns`

- **Lazy Imports**: [`__init__.py`](__init__.py) minimizes startup dependencies
- **Type Safety**: Extensive use of Pydantic models and type hints
- **Error Handling**: Comprehensive exception handling with timeouts
- **Testing**: Module-specific tests in [`../tests/`](../tests/)

**Architecture Principle**: Each module is self-contained with minimal cross-dependencies, enabling selective imports and reduced memory footprint.

---

**Parent Documentation**: See [main README](../../README.md) for installation and usage patterns.