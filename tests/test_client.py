"""A2A integration test client for the Alpha Vantage agent.

Requires the agent server to be running on AGENT_PORT (default: 10000).
Run with: task test:a2a
"""

import asyncio
import os
import sys

import httpx
from a2a.client import A2AClient
from a2a.types import SendMessageRequest, MessageSendParams


AGENT_PORT = int(os.getenv("AGENT_PORT", 10000))
AGENT_BASE_URL = f"http://localhost:{AGENT_PORT}"

SCENARIOS = [
    {
        "name": "single_turn_stock_quote",
        "message": "What is the current stock price of Microsoft (MSFT)?",
    },
    {
        "name": "single_turn_company_overview",
        "message": "Give me a brief fundamental overview of Apple (AAPL).",
    },
    {
        "name": "multi_turn_followup",
        "messages": [
            "What is the stock price of NVDA?",
            "Now compare it to AMD.",
        ],
    },
]


async def fetch_agent_card(client: httpx.AsyncClient) -> dict:
    resp = await client.get(f"{AGENT_BASE_URL}/.well-known/agent-card.json")
    resp.raise_for_status()
    card = resp.json()
    print(f"[agent card] name={card.get('name')} url={card.get('url')}")
    return card


async def run_single_turn(a2a: A2AClient, message: str, scenario: str) -> None:
    print(f"\n[scenario:{scenario}] >>> {message}")
    request = SendMessageRequest(
        params=MessageSendParams(message={"role": "user", "parts": [{"text": message}]})
    )
    response = await a2a.send_message(request)
    result = response.root

    text_parts = []
    token_info = {}

    if hasattr(result, "result") and result.result:
        task = result.result
        if hasattr(task, "artifacts") and task.artifacts:
            for artifact in task.artifacts:
                if hasattr(artifact, "parts"):
                    for part in artifact.parts:
                        if hasattr(part.root, "text"):
                            text_parts.append(part.root.text)
        if hasattr(task, "metadata") and task.metadata:
            token_info = task.metadata.get("adk_usage_metadata", {})

    reply = " ".join(text_parts) if text_parts else "(no text response)"
    print(f"[scenario:{scenario}] <<< {reply[:200]}{'...' if len(reply) > 200 else ''}")
    if token_info:
        print(f"[scenario:{scenario}] tokens={token_info}")

    assert reply != "(no text response)", f"Scenario '{scenario}' returned no text"


async def run_multi_turn(a2a: A2AClient, messages: list[str], scenario: str) -> None:
    for i, message in enumerate(messages):
        await run_single_turn(a2a, message, f"{scenario}_turn{i + 1}")


async def main() -> int:
    print(f"Connecting to agent at {AGENT_BASE_URL}")

    async with httpx.AsyncClient(timeout=120.0) as http_client:
        try:
            card = await fetch_agent_card(http_client)
        except httpx.ConnectError:
            print(
                f"ERROR: Could not connect to agent at {AGENT_BASE_URL}. "
                "Is the server running? (task up:agent)"
            )
            return 1

        a2a = await A2AClient.get_client_from_agent_card_url(
            http_client, f"{AGENT_BASE_URL}/.well-known/agent-card.json"
        )

        failed = 0
        for scenario in SCENARIOS:
            try:
                if "messages" in scenario:
                    await run_multi_turn(a2a, scenario["messages"], scenario["name"])
                else:
                    await run_single_turn(a2a, scenario["message"], scenario["name"])
            except Exception as exc:
                print(f"[scenario:{scenario['name']}] FAILED: {exc}")
                failed += 1

    if failed:
        print(f"\n{failed} scenario(s) failed.")
        return 1

    print(f"\nAll {len(SCENARIOS)} scenario(s) passed.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
