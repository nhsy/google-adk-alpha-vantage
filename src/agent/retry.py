import logging

import structlog
from tenacity import (
    after_log,
    before_sleep_log,
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
)

logger = structlog.get_logger(__name__)

agent_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=3, max=60),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    after=after_log(logger, logging.ERROR),
    reraise=True,
)
