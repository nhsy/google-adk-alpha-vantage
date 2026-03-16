# Alpha Vantage Agent (ADK + A2A + MCP)

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-ADK-4285F4.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAhGVYSWZNTQAqAAAACAAFARIAAwAAAAEAAQAAARoABQAAAAEAAABKARsABQAAAAEAAABSASgAAwAAAAEAAgAAh2kABAAAAAEAAABaAAAAAAAAAEgAAAABAAAASAAAAAEAA6ABAAMAAAABAAEAAKACAAQAAAABAAAADqADAAQAAAABAAAADgAAAABOylT5AAAACXBIWXMAAAsTAAALEwEAmpwYAAABWWlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNi4wLjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyI+CiAgICAgICAgIDx0aWZmOk9yaWVudGF0aW9uPjE8L3RpZmY6T3JpZW50YXRpb24+CiAgICAgIDwvcmRmOkRlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgoZXuEHAAACRUlEQVQoFXVSS2gTQRj+Z3aziUlF1ISkRqqpVpCaixgkkEOaUGktBopuRQXxKF68pIdCpSsYH4gWxINHT8ZmVUR7MaRND4pUFBFfB7GXqt1iAlGS5rn7O7NpFg/6HeZ/zPfN/PMxAOtQFKSd/L8RFYtDOEmWUVBVovM8fgHDDc+iv+I9VxcgAAhdEtUbP16dTL80uRlZUMdUnXREPBb3/7pDm65g1f3iS9094QRjOwBZWwO09REQ3++kD86qY6DLTAydEWOXy8lYqpzjp/4LB+4fzYVmjiXNPTYyVRRi8IIgRijqk4eua65YqnJLzqDA+wPXijdOALpbzocTaHRFeA+IYliPZaVGCD2cHfdVCJRT6lj7zS1dupoGUhCrsREgVc0Ucm1UQXFBIa3IlVJvU5ceiQTmNyPmddR9DbAZur28Wt1xJi4YjiFq2Eeen7q3FM1HGY2DGQPM1dM3C/5izZ6sGdA9Jzm1YAOc2xzfNj3bNfUJ9t2dhj74DRkQgBlk6vhSy+49b8zBG1wBD69xD4wiQI+Zg/dIHUL97Twq8mi9UaSfo03snSXd8HMlkbitBYbGPxyftHHS99HdW0qDkC4MhOIEFlqoALWEhuGoEVia5UQbLCdoffVdcObSV15v1EpPmfdbkWDbVdazhJQ2KwSlx7gIAfeTtz1EEv3F+MFBLqw7nVNIYNoz//oiG5+Cwj4UIpgGYR58tayQwJzLy8kcODxs53E5HN7AI4fy12WW2Nxhy0e5X+rk7Ia286yBMvtq6/gDb7bjW6TkRnEAAAAASUVORK5CYII=)](https://github.com/google/adk-python)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

A sample agent demonstrating ADK + A2A + MCP working together for financial data analysis. It leverages Google's **Agent Development Kit (ADK)**, [`google-adk`](https://github.com/google/adk-python), and the **Agent2Agent (A2A) Python SDK** ([`a2a-sdk`](https://github.com/google-a2a/a2a-python)).

## Overview

This project builds a demo for integrating [Alpha Vantage's](https://www.alphavantage.co/) financial data into agentic workflows. It showcases how MCP, ADK, and A2A can be composed to create a capable financial data agent that can query stock prices, forex rates, cryptocurrency data, technical indicators, and macroeconomic data.

### Model Context Protocol (MCP)

> MCP is an open protocol that standardizes how applications provide context to LLMs. Think of MCP like a USB-C port for AI applications. Just as USB-C provides a standardized way to connect your devices to various peripherals and accessories, MCP provides a standardized way to connect AI models to different data sources and tools. - [Anthropic](https://modelcontextprotocol.io/introduction)

The agents connect directly to the [Alpha Vantage MCP server](https://mcp.alphavantage.co/) over HTTP. The MCP server exposes a broad set of financial tools spanning stocks, forex, cryptocurrency, technical indicators, economic indicators, and market intelligence.

### Agent Development Kit (ADK)

> ADK is a flexible and modular framework for developing and deploying AI agents. While optimized for Gemini and the Google ecosystem, ADK is model-agnostic, deployment-agnostic, and is built for compatibility with other frameworks. - [ADK](https://github.com/google/adk-python)

ADK serves as the orchestration framework for the agents in this project. It manages conversation state, invokes MCP tools when needed, and supports multi-agent workflows via the A2A protocol.

### Agent2Agent (A2A)

> Agent2Agent (A2A) protocol addresses a critical challenge in the AI landscape: enabling gen AI agents, built on diverse frameworks by different companies running on separate servers, to communicate and collaborate effectively — as agents, not just as tools. - [A2A](https://github.com/a2aproject/A2A)

The [A2A Python SDK](https://github.com/google-a2a/a2a-python) is used to expose the ADK agent as an A2A-compatible service. A second entry point (`scripts/a2a_demo.py`) demonstrates a multi-agent workflow where a **Research Agent** gathers raw financial data and an **Analyst Agent** interprets and summarizes the results.

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation) for dependency management
- [Task](https://taskfile.dev/) for automation
- An [Alpha Vantage API key](https://www.alphavantage.co/support/#api-key)
- A [Google AI Studio API key](https://aistudio.google.com/apikey) **or** a Google Cloud project with [Vertex AI](https://cloud.google.com/vertex-ai) enabled
- Git, for cloning the repository.

### Installation

1. Clone the repository:

```bash
git clone https://github.com/nhsy/google-adk-alpha-vantage.git
cd google-adk-alpha-vantage
```

2. Initialize the project:

```bash
task init
```

This installs all Python dependencies and sets up pre-commit hooks.

3. Configure environment variables (via `.env` file):

Copy `.env.example` to `.env` and fill in the required values:

```bash
cp .env.example .env
```

There are two different ways to call Gemini models:

- Calling the Gemini API directly using an API key created via Google AI Studio.
- Calling Gemini models through Vertex AI APIs on Google Cloud.

> [!TIP]
> An API key from Google AI Studio is the quickest way to get started.
>
> Existing Google Cloud users may want to use Vertex AI.

<details open>
<summary>Gemini API Key</summary>

Get an API Key from Google AI Studio: https://aistudio.google.com/apikey

Set the following values in your `.env` file:

```sh
GOOGLE_API_KEY=<your_api_key_here>
GOOGLE_GENAI_USE_VERTEXAI=FALSE
ALPHA_VANTAGE_API_KEY=<your_alpha_vantage_key_here>
```

</details>

<details>
<summary>Vertex AI</summary>

To use Vertex AI, you will need to [create a Google Cloud project](https://developers.google.com/workspace/guides/create-project) and [enable Vertex AI](https://cloud.google.com/vertex-ai/docs/start/cloud-environment).

Authenticate and enable the Vertex AI API:

```bash
gcloud auth login
# Replace <your_project_id> with your project ID
gcloud config set project <your_project_id>
gcloud services enable aiplatform.googleapis.com
```

Set the following values in your `.env` file:

```sh
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=<your_project_id>
GOOGLE_CLOUD_LOCATION=us-central1
ALPHA_VANTAGE_API_KEY=<your_alpha_vantage_key_here>
```

</details>

## Automation with Taskfile

This project uses [Task](https://taskfile.dev/) for automation. The following commands are available:

- `task init`: Initialize the project (install dependencies, install pre-commit hooks).
- `task deps`: Check for required dependencies (uv, python).
- `task lint`: Run linting and formatting checks (ruff).
- `task up`: Start all servers (agent, ADK workbench).
- `task up:agent`: Start the A2A Agent Server.
- `task up:adk`: Start the ADK Workbench (web UI).
- `task down`: Stop all servers.
- `task demo`: Run the demo script (four sample queries).
- `task demo:a2a`: Run the A2A multi-agent demo.
- `task agent:card`: Fetch and display the A2A agent card.
- `task test`: Run all unit tests.
- `task test:cov`: Run tests with coverage reporting.
- `task test:a2a`: Run A2A integration tests against the live agent server (requires `task up:agent`).

## Local Deployment

### Agent Server

In a terminal, start the A2A Agent Server (starts on port 10000):

```bash
task up:agent
```

### ADK Workbench (Web UI)

In a separate terminal, start the ADK Workbench to interact with the agent via a web interface (starts on port 8000):

```bash
task up:adk
```

### Agent Card

To inspect the A2A agent card advertised by the agent server:

```bash
task agent:card
```

### Demo Script

To run a set of sample financial queries against the agent:

```bash
task demo
```

### A2A Multi-Agent Demo

To run the multi-agent workflow (Research Agent + Analyst Agent):

```bash
task demo:a2a
```

### Cleanup

To stop all servers and free up their ports:

```bash
task down
```

## Logging

This project uses [structlog](https://www.structlog.org/) for structured logging. By default, logs are rendered in a human-readable format for the console.

To enable JSON structured logging (useful for production environments or log aggregation), set the `LOG_JSON` environment variable to `TRUE`:

```bash
export LOG_JSON=TRUE
task up
```

## Disclaimer

This project is intended solely as a demonstration of how Google ADK, the A2A protocol, and the Alpha Vantage MCP server can be composed into an agentic workflow. The financial data and analysis produced by this agent should not be relied upon for investment decisions or any other financial purpose. Use at your own risk.

## Contributing

Contributions are welcome. Please feel free to submit pull requests or open issues.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.
