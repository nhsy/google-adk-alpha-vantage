import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
MCP_URL = f"https://mcp.alphavantage.co/mcp?apikey={_api_key}"

# 1. Research Agent: Specialized in gathering raw data
research_agent = LlmAgent(
    model=os.getenv("AGENT_GEMINI_MODEL", "gemini-2.5-flash"),
    name="research_agent",
    description="Gathers financial data and news using Alpha Vantage tools.",
    instruction=(
        "You are a Financial Research Agent. Your sole job is to gather data.\n"
        "Use 'global_quote', 'company_overview', 'earnings', and 'news_sentiment' to collect facts.\n"
        "Provide raw, structured data to the Analyst Agent. Do not interpret the data yourself."
    ),
    tools=[McpToolset(connection_params=StreamableHTTPConnectionParams(url=MCP_URL))],
)

# 2. Analyst Agent: Specialized in interpreting data
analyst_agent = LlmAgent(
    model=os.getenv("AGENT_GEMINI_MODEL", "gemini-2.5-flash"),
    name="analyst_agent",
    description="Analyzes financial data gathered by the research agent.",
    instruction=(
        "You are a Senior Financial Analyst. Your job is to interpret data provided by the Research Agent.\n"
        "Analyze trends, earnings performance, and news sentiment to provide a buy/sell/hold recommendation.\n"
        "If you need more data, ask the Research Agent specifically for it."
    ),
)
