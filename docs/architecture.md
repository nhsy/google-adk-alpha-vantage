# Architecture

This document describes the architecture of the Alpha Vantage Agent, covering the agent hierarchy, protocol integrations, data flow, and key implementation details.

## High-Level Overview

The system is composed of three protocol layers working together:

1. **MCP (Model Context Protocol)** provides standardized access to the Alpha Vantage financial data APIs.
2. **ADK (Agent Development Kit)** orchestrates agent logic, tool invocation, and conversation state.
3. **A2A (Agent2Agent)** exposes agents as network services that can communicate with each other.

### Workflow Diagram

<p align="center">
  <img src="workflow.png" alt="Alpha Vantage Agent Workflow Architecture" width="100%">
</p>

## Agent Hierarchy

### Root Agent

The `root_agent` (`src/agent/main.py`) is the primary entry point for all user interactions. It is an ADK `LlmAgent` configured with:

- **Model**: `gemini-2.5-flash` (configurable via `AGENT_GEMINI_MODEL`)
- **System instruction**: A detailed prompt covering all Alpha Vantage tool categories, usage guidelines, and rate-limiting awareness.
- **Tools**:
  - `McpToolset` -- dynamically exposes all Alpha Vantage MCP tools (stock quotes, company overviews, earnings, forex, crypto, technical indicators, economic indicators, and market intelligence).
  - `get_current_datetime` -- provides current UTC date and time so the agent can compute date ranges for API queries.
  - `ticker_resolver_tool` -- an `AgentTool` wrapping the ticker resolver sub-agent.

### Ticker Resolver Sub-Agent

The `ticker_resolver_agent` (`src/agent/ticker_resolver.py`) resolves company names to stock ticker symbols. When a user says "Microsoft" instead of "MSFT", the root agent delegates to this sub-agent, which uses the ADK built-in `google_search` tool to look up the correct ticker symbol.

### Multi-Agent Workflow (A2A Demo)

The A2A demo (`src/a2a/main.py`) defines two specialized agents that operate in sequence:

| Agent | Role | Tools |
|-------|------|-------|
| `research_agent` | Gathers raw financial data (prices, earnings, sentiment) | `McpToolset` (Alpha Vantage) |
| `analyst_agent` | Interprets data and provides buy/sell/hold recommendations | None (receives data as context) |

```
User Query
    │
    ▼
research_agent ──► Alpha Vantage MCP ──► Raw Data
    │
    ▼
analyst_agent ──► Investment Recommendation
```

## MCP Integration

The agents connect to the [Alpha Vantage MCP server](https://mcp.alphavantage.co/) over HTTP using ADK's `McpToolset` with `StreamableHTTPConnectionParams`:

```python
toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=f"https://mcp.alphavantage.co/mcp?apikey={api_key}"
    )
)
```

The MCP server exposes tools spanning:

- **Core stock APIs**: `GLOBAL_QUOTE`, `TIME_SERIES_INTRADAY`, `TIME_SERIES_DAILY`, etc.
- **Fundamental data**: `COMPANY_OVERVIEW`, `EARNINGS`, financial statements
- **Alpha intelligence**: `NEWS_SENTIMENT`
- **Forex and cryptocurrencies**: Exchange rates and digital asset data
- **Economic indicators**: GDP, unemployment, and other macroeconomic data
- **Technical indicators**: SMA, RSI, MACD, and more

The toolset dynamically discovers available tools from the MCP server at startup, so no manual tool registration is required.

## A2A Integration

The root agent is exposed as an A2A-compatible service via ADK's `to_a2a()` utility (`src/agent/__main__.py`):

```python
a2a_app = to_a2a(root_agent, port=port)
```

This wraps the agent as a FastAPI application with two key endpoints:

- `GET /.well-known/agent-card.json` -- advertises the agent's capabilities for discovery by other agents or clients.
- `POST /` -- accepts A2A `SendMessageRequest` payloads and returns agent responses.

The server runs on `uvicorn` (default port 10000) and handles graceful shutdown by closing the MCP toolset connection.

## Data Flow

### Single-Agent Query

```
1. User sends query (e.g., "What is the price of NVIDIA?")
2. root_agent identifies "NVIDIA" as a company name
3. root_agent invokes ticker_resolver_tool → ticker_resolver_agent
4. ticker_resolver_agent uses google_search → returns "NVDA"
5. root_agent invokes MCP tool GLOBAL_QUOTE(symbol="NVDA")
6. Alpha Vantage MCP server returns price data
7. root_agent generates natural language response
```

### Multi-Agent Workflow

```
1. User provides a stock symbol (e.g., "AAPL")
2. research_agent calls GLOBAL_QUOTE, COMPANY_OVERVIEW, EARNINGS, NEWS_SENTIMENT
3. research_agent returns raw financial data as text
4. analyst_agent receives the research text as context
5. analyst_agent produces an investment recommendation
```

## Entry Points

| Entry Point | Command | Description |
|-------------|---------|-------------|
| A2A Agent Server | `task up:agent` | Starts the agent as an A2A service on port 10000 |
| ADK Workbench | `task up:adk` | Starts the web UI on port 8000 |
| Agent Demo | `task demo:agent` | Runs four sample financial queries against the agent |
| A2A Demo | `task demo:a2a` | Runs the research + analyst multi-agent workflow |

## Resilience

### Retry Logic

The `agent_retry` decorator (`src/agent/retry.py`) uses `tenacity` to handle transient failures:

- **Max attempts**: 3
- **Backoff**: Exponential with jitter (initial 3s, max 60s)
- **Logging**: Warns before retry sleep, logs errors on failed attempts

This is applied to agent execution in the demo scripts to handle Alpha Vantage rate limits and intermittent network issues.

### Rate Limiting

Alpha Vantage's free tier allows 1 request per 3 seconds. This is addressed at multiple levels:

- The root agent's system instruction documents the rate limit so the model avoids rapid consecutive calls.
- Demo scripts introduce a 3-second delay between queries.
- The retry decorator provides automatic backoff when rate-limit errors occur.

## Logging

The project uses [structlog](https://www.structlog.org/) with two rendering modes:

- **Console** (default): Human-readable, colored output for development.
- **JSON** (`LOG_JSON=TRUE`): Machine-parseable output for production and log aggregation.

Logged events include server lifecycle (`agent_server_started`, `agent_server_stopped`), task execution (`agent_task_started`, `agent_task_completed`, `agent_task_failed`), and demo workflow phases.

## Project Structure

```
.
├── src/
│   ├── agent/
│   │   ├── __init__.py          # Exports root_agent
│   │   ├── __main__.py          # A2A server entry point
│   │   ├── main.py              # Root agent definition, MCP toolset setup
│   │   ├── retry.py             # Tenacity retry decorator
│   │   ├── ticker_resolver.py   # Ticker resolver sub-agent
│   │   └── tools.py             # get_current_datetime utility tool
│   └── a2a/
│       └── main.py              # Research + analyst agents for multi-agent demo
├── scripts/
│   ├── agent_demo.py            # Standalone agent demo (4 queries)
│   └── a2a_demo.py              # Multi-agent workflow demo
├── tests/
│   ├── test_agent.py            # Agent configuration and execution tests
│   ├── test_tools.py            # DateTime tool unit tests
│   ├── test_retry.py            # Retry logic tests
│   ├── test_a2a_demo.py         # Multi-agent workflow test
│   └── test_client.py           # A2A integration tests (requires running server)
├── docs/
│   └── architecture.md          # This file
├── Taskfile.yml                 # Task automation
├── pyproject.toml               # Dependencies and project metadata
└── .env.example                 # Environment variable template
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `google-adk[a2a]` | Agent framework with A2A protocol support |
| `a2a-sdk` | A2A client and server SDK |
| `tenacity` | Retry logic with exponential backoff |
| `structlog` | Structured, context-aware logging |
| `uvicorn` | ASGI server for the A2A agent service |
| `ruff` | Linting and formatting |
| `pytest` / `pytest-asyncio` / `pytest-cov` | Testing framework |
