import os

from google.adk.agents import LlmAgent
from google.adk.tools import google_search

TICKER_RESOLVER_INSTRUCTION = (
    "You are a stock ticker symbol resolver. "
    "When given a company name, use google_search to find its official stock ticker symbol. "
    "Search for '<company name> stock ticker symbol site:finance.yahoo.com OR site:google.com/finance'. "
    "Return only the ticker symbol as plain text (e.g. 'INTC' for Intel, 'AAPL' for Apple). "
    "Do not include any explanation, punctuation, or extra text — just the ticker."
)

ticker_resolver_agent = LlmAgent(
    model=os.getenv("AGENT_GEMINI_MODEL", "gemini-2.5-flash"),
    name="ticker_resolver",
    description="Resolves a company name to its stock ticker symbol using Google Search.",
    instruction=TICKER_RESOLVER_INSTRUCTION,
    tools=[google_search],
)
