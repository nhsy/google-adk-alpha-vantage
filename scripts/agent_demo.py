import asyncio
import warnings
import structlog
import logging
from src.agent.main import root_agent
from src.agent.retry import agent_retry
from google.adk.runners import InMemoryRunner
from google.genai import types as genai_types

warnings.filterwarnings("ignore", message=r".*\[EXPERIMENTAL\].*")
warnings.filterwarnings("ignore", message=r".*non-text parts.*")

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


@agent_retry
async def run_agent(agent, query):
    """Helper to run an agent and return the final text response."""
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


async def run_analysis_demo():
    print("\n" + "=" * 50)
    print("ALPHA VANTAGE ADK AGENT DEMO")
    print("=" * 50 + "\n")

    queries = [
        "What is the current stock price and trading volume for NVIDIA (NVDA)?",
        "Give me a fundamental overview of Microsoft (MSFT), including its P/E ratio and sector.",
        "What is the current market sentiment for Tesla (TSLA) according to recent news?",
        "Compare the earnings performance of Apple (AAPL) and Google (GOOGL) over the last few quarters.",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\nQuery {i}: {query}")
        logger.info("agent_task_started", query=query)

        try:
            response_text = await run_agent(root_agent, query)
            print(f"\nAgent Response:\n{response_text}\n")
            logger.info("agent_task_completed", status="success")
        except Exception as e:
            logger.error("agent_task_failed", error=str(e))
            print(f"\nError: {e}\n")

        if i < len(queries):
            print("-" * 30)
            await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(run_analysis_demo())
