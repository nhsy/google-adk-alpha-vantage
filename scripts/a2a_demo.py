import asyncio
import warnings
import structlog
import logging
from dotenv import load_dotenv
from src.a2a.main import research_agent, analyst_agent
from google.adk.runners import InMemoryRunner
from google.genai import types as genai_types

warnings.filterwarnings("ignore", message=r".*non-text parts.*")

load_dotenv()

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)
logger = structlog.get_logger(__name__)


async def run_agent(agent, query):
    """Helper to run an agent using InMemoryRunner and return final text."""
    runner = InMemoryRunner(agent=agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="demo_user"
    )
    new_message = genai_types.Content(parts=[genai_types.Part(text=query)])
    final_text = ""
    async for event in runner.run_async(
        user_id="demo_user", session_id=session.id, new_message=new_message
    ):
        if event.is_final_response() and event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_text += part.text
    return final_text


async def run_demo(symbol: str = "AAPL"):
    logger.info("demo_started", symbol=symbol)

    research_query = f"Gather the latest price, overview, and sentiment for {symbol}."
    logger.info("research_step_started", query=research_query)
    research_text = await run_agent(research_agent, research_query)
    logger.info("research_step_completed", response=research_text[:200] + "...")

    analyst_query = f"Based on this research: '{research_text}', provide a summary analysis and recommendation for {symbol}."
    logger.info("analysis_step_started")
    analyst_text = await run_agent(analyst_agent, analyst_query)
    logger.info("analysis_step_completed", recommendation=analyst_text)
    return analyst_text


if __name__ == "__main__":
    asyncio.run(run_demo())
