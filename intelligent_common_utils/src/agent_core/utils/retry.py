"""Retry with exponential backoff for external API calls."""

import asyncio
import logging
import random
from collections.abc import Awaitable, Callable
from typing import Optional, TypeVar, Tuple, Type

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def with_retry(
    fn: Callable[[], Awaitable[T]],
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retry_exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> T:
    """
    Run async fn with exponential backoff. Retries on retry_exceptions.
    """
    last_exc: Optional[Exception] = None
    for attempt in range(max_attempts):
        try:
            return await fn()
        except retry_exceptions as e:
            last_exc = e
            if attempt == max_attempts - 1:
                logger.error("Retry exhausted after %s attempts: %s", max_attempts, e)
                raise
            delay = min(base_delay * (2**attempt) + random.uniform(0, 1), max_delay)
            logger.warning("Attempt %s failed: %s; retrying in %.2fs", attempt + 1, e, delay)
            await asyncio.sleep(delay)
    raise last_exc  # type: ignore[misc]
