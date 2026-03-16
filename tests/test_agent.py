import os
import pytest
from unittest.mock import patch, MagicMock
from src.agent.main import root_agent
from src.agent.tools import get_current_datetime
from google.adk.tools.mcp_tool import McpToolset


def test_agent_properties():
    """Verify core properties of the Alpha Vantage agent."""
    assert root_agent.name == "alpha_vantage_agent"
    assert "Alpha Vantage Financial Analysis Assistant" in root_agent.instruction
    assert len(root_agent.tools) == 2
    assert isinstance(root_agent.tools[0], McpToolset)
    assert root_agent.tools[1] is get_current_datetime


def test_mcp_toolset_config():
    """Verify that the MCP toolset is configured with the Alpha Vantage MCP URL."""
    toolset = root_agent.tools[0]
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    expected_url = f"https://mcp.alphavantage.co/mcp?apikey={api_key}"
    assert toolset._connection_params.url == expected_url


def test_a2a_conversion():
    """Verify that the agent can be converted to an A2A-compatible app."""
    from google.adk.a2a.utils.agent_to_a2a import to_a2a

    a2a_app = to_a2a(root_agent, port=10000)
    assert a2a_app is not None
    assert hasattr(a2a_app, "router")


@pytest.mark.asyncio
async def test_agent_execution():
    """Verify that the agent's run method can be called (mocked)."""
    from unittest.mock import AsyncMock
    from scripts.agent_demo import run_agent as run_agent_helper

    mock_part = MagicMock()
    mock_part.text = "Analysis complete."
    mock_event = MagicMock()
    mock_event.is_final_response.return_value = True
    mock_event.content.parts = [mock_part]

    async def mock_run_async(self, **kwargs):
        yield mock_event

    mock_runner = MagicMock()
    mock_runner.app_name = "test_app"
    mock_runner.session_service.create_session = AsyncMock(
        return_value=MagicMock(id="test-session")
    )
    mock_runner.run_async = lambda **kwargs: mock_run_async(mock_runner, **kwargs)

    with patch("scripts.agent_demo.InMemoryRunner", return_value=mock_runner):
        response_text = await run_agent_helper(root_agent, "What is the price of AAPL?")
        assert response_text == "Analysis complete."


def test_system_instruction_content():
    """Verify that key financial analysis instructions are present."""
    instruction = root_agent.instruction
    assert "core_stock_apis" in instruction
    assert "fundamental_data" in instruction
    assert "GLOBAL_QUOTE" in instruction
    assert "COMPANY_OVERVIEW" in instruction
    assert "NEWS_SENTIMENT" in instruction
    assert "3 seconds" in instruction


def test_missing_api_key_raises(monkeypatch):
    import importlib
    import src.agent.main as agent_main

    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "")
    with pytest.raises(ValueError, match="ALPHA_VANTAGE_API_KEY"):
        importlib.reload(agent_main)
