import pytest
from unittest.mock import patch, AsyncMock
from scripts.a2a_demo import run_demo


@pytest.mark.asyncio
async def test_run_demo_flow():
    """Verify the core logic of the A2A demo by mocking agent runs."""
    with patch("scripts.a2a_demo.run_agent", new_callable=AsyncMock) as mock_run:
        mock_run.side_effect = [
            "Raw data for AAPL",
            "Recommendation: Buy",
        ]

        result = await run_demo(symbol="AAPL")

        assert result == "Recommendation: Buy"
        assert mock_run.call_count == 2
