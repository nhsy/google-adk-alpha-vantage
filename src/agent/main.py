import os
import warnings
import structlog
import logging

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

# Suppress warnings about experimental features (module filter + message filter
# for warnings re-raised with stacklevel=2 that appear to originate from user code)
warnings.filterwarnings("ignore", category=UserWarning, module=r"google\.adk")
warnings.filterwarnings("ignore", message=r"\[EXPERIMENTAL\]", category=UserWarning)

# Configure structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
        if not os.getenv("LOG_JSON")
        else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

load_dotenv()

_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
MCP_URL = f"https://mcp.alphavantage.co/mcp?apikey={_api_key}"

SYSTEM_INSTRUCTION = (
    "You are a specialized Alpha Vantage Financial Analysis Assistant. "
    "Your goal is to provide accurate stock market data, fundamental insights, and financial trends using the provided Alpha Vantage tools.\n\n"
    "TOOLS:\n"
    "The Alpha Vantage MCP server provides tools across several categories:\n"
    "1. 'core_stock_apis': Real-time and historical stock quotes (e.g., 'GLOBAL_QUOTE', 'TIME_SERIES_INTRADAY').\n"
    "2. 'fundamental_data': Company metrics, earnings, and financial statements (e.g., 'COMPANY_OVERVIEW', 'EARNINGS').\n"
    "3. 'alpha_intelligence': Market news and sentiment analysis (e.g., 'NEWS_SENTIMENT').\n"
    "4. 'forex' and 'cryptocurrencies': Exchange rates for traditional and digital currencies.\n"
    "5. 'economic_indicators' and 'technical_indicators': Broad market data and analytical indicators (e.g., 'SMA', 'REAL_GDP').\n\n"
    "GUIDELINES:\n"
    "- CORE QUOTES: For simple price checks, always use 'GLOBAL_QUOTE'.\n"
    "- FUNDAMENTAL ANALYSIS: When asked about a company's health or financial status, use 'COMPANY_OVERVIEW' and 'EARNINGS'.\n"
    "- SENTIMENT: Use 'NEWS_SENTIMENT' to gauge the current market mood for a specific ticker.\n"
    "- CLARITY: Map informal company names to stock symbols (e.g., 'Apple' to 'AAPL') using 'SYMBOL_SEARCH' if the symbol is not provided.\n"
    "- RATE LIMIT: The Alpha Vantage API enforces a rate limit of 1 request per 3 seconds on free-tier keys. "
    "Wait at least 3 seconds between consecutive tool calls to avoid errors.\n"
    "- SCOPE: Only assist with financial and stock-market related queries. Politely decline all other topics."
)

logger.info("--- 🔧 Loading Alpha Vantage MCP tools... ---")
logger.info("--- 🤖 Creating ADK Alpha Vantage Agent... ---")

# Initialize the toolset pointing to the Alpha Vantage MCP server
toolset = McpToolset(connection_params=StreamableHTTPConnectionParams(url=MCP_URL))

root_agent = LlmAgent(
    model=os.getenv("AGENT_GEMINI_MODEL", "gemini-2.5-flash"),
    name="alpha_vantage_agent",
    description="An agent that provides financial data and stock analysis using Alpha Vantage.",
    instruction=SYSTEM_INSTRUCTION,
    tools=[toolset],
)

if __name__ == "__main__":
    import asyncio
    import uvicorn
    from google.adk.a2a.utils.agent_to_a2a import to_a2a

    port = int(os.getenv("AGENT_PORT", 10000))
    a2a_app = to_a2a(root_agent, port=port)

    async def serve():
        config = uvicorn.Config(a2a_app, host="localhost", port=port)
        server = uvicorn.Server(config)
        logger.info("agent_server_started", port=port)
        try:
            await server.serve()
        finally:
            logger.info("agent_server_stopping")
            await toolset.close()
            logger.info("agent_server_stopped")

    asyncio.run(serve())
