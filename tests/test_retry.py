import pytest
from unittest.mock import AsyncMock

from src.agent.retry import agent_retry


async def _make_flaky(responses):
    """Return an async function that yields responses in order (raise if Exception)."""

    async def fn():
        resp = responses.pop(0)
        if isinstance(resp, Exception):
            raise resp
        return resp

    return fn


class TestAgentRetry:
    @pytest.mark.asyncio
    async def test_succeeds_on_first_attempt(self):
        mock = AsyncMock(return_value="ok")
        decorated = agent_retry(mock)

        result = await decorated()

        assert result == "ok"
        assert mock.call_count == 1

    @pytest.mark.asyncio
    async def test_retries_on_transient_failure_and_succeeds(self):
        mock = AsyncMock(side_effect=[RuntimeError("transient"), "ok"])
        decorated = agent_retry(mock)

        result = await decorated()

        assert result == "ok"
        assert mock.call_count == 2

    @pytest.mark.asyncio
    async def test_raises_after_all_attempts_exhausted(self):
        err = RuntimeError("persistent")
        mock = AsyncMock(side_effect=[err, err, err])
        decorated = agent_retry(mock)

        with pytest.raises(RuntimeError, match="persistent"):
            await decorated()

        assert mock.call_count == 3

    @pytest.mark.asyncio
    async def test_correct_call_count_on_second_attempt_success(self):
        responses = [ValueError("first fail"), ValueError("second fail"), "success"]
        mock = AsyncMock(side_effect=responses)
        decorated = agent_retry(mock)

        result = await decorated()

        assert result == "success"
        assert mock.call_count == 3
