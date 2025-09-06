"""Retry policy implementation for handling transient failures.

This module provides configurable retry strategies with exponential backoff,
status code-based retries, and support for idempotent vs non-idempotent methods.
"""

import random
from http import HTTPStatus
from typing import Callable, NamedTuple

from ..enums import HttpMethod, RetryDecision as RetryDecisionEnum


class RetryDecision(NamedTuple):
    """Retry decision with optional delay.

    Attributes:
        decision: Whether to retry or give up.
        delay_seconds: Delay in seconds before retry, or None if giving up.
    """

    decision: RetryDecisionEnum
    delay_seconds: float | None


RetryStrategy = Callable[[int, str, str, int | None, BaseException | None], RetryDecision]
# args: attempt_no (1-based), method, url, status (or None), exception (or None)


def default_retry_strategy(
    max_attempts: int = 3,
    base_delay: float = 0.25,
    allow_non_idempotent: bool = False,
) -> RetryStrategy:
    """Create a default retry strategy with exponential backoff.

    This strategy implements the following retry logic:
    - Retries on network/connection errors (exceptions)
    - Retries on HTTP status codes: 429 (rate limit), 500-504 (server errors)
    - Only retries non-idempotent methods (POST, PUT, DELETE, PATCH) if allow_non_idempotent=True
    - Uses exponential backoff with jitter: delay = base_delay * (2 ^ attempt) + random_jitter
    - Maximum delay capped at 60 seconds to prevent excessive waits
    - Gives up after max_attempts total attempts

    Args:
        max_attempts: Maximum number of retry attempts (default 3). Must be >= 1.
        base_delay: Base delay in seconds for exponential backoff (default 0.25). Must be > 0.
        allow_non_idempotent: Whether to retry non-idempotent methods (default False).
                            WARNING: Only enable for idempotent operations.

    Returns:
        A retry strategy function that takes (attempt, method, url, status, exception)
        and returns RetryDecision.

    Raises:
        ValueError: If max_attempts < 1 or base_delay <= 0.

    Example:
        # Default strategy
        strategy = default_retry_strategy()

        # Custom strategy with more attempts
        strategy = default_retry_strategy(max_attempts=5, base_delay=1.0)

        # Allow retries for non-idempotent methods
        strategy = default_retry_strategy(allow_non_idempotent=True)
    """
    # Input validation
    if max_attempts < 1:
        raise ValueError(f"max_attempts must be >= 1, got {max_attempts}")
    if base_delay <= 0:
        raise ValueError(f"base_delay must be > 0, got {base_delay}")

    IDEMPOTENT = {HttpMethod.GET.value, HttpMethod.HEAD.value, HttpMethod.OPTIONS.value}
    RETRYABLE_STATUS = {
        HTTPStatus.TOO_MANY_REQUESTS,  # 429
        HTTPStatus.INTERNAL_SERVER_ERROR,  # 500
        HTTPStatus.BAD_GATEWAY,  # 502
        HTTPStatus.SERVICE_UNAVAILABLE,  # 503
        HTTPStatus.GATEWAY_TIMEOUT,  # 504
    }

    def _strategy(
        attempt: int,
        method: str,
        url: str,
        status: int | None,
        exc: BaseException | None,
    ) -> RetryDecision:
        """Default retry strategy implementation.

        Args:
            attempt: Current attempt number (1-based).
            method: HTTP method.
            url: Request URL.
            status: HTTP status code (None if exception occurred).
            exc: Exception that occurred (None if status code available).

        Returns:
            RetryDecision indicating whether to retry and with what delay.
        """
        if attempt >= max_attempts:
            return RetryDecision(RetryDecisionEnum.GIVE_UP, None)
        if exc is not None:
            # network/connect/read timeouts etc. → retry
            delay = base_delay * (2 ** (attempt - 1))
            # Cap delay at 60 seconds to prevent excessive waits
            total_delay = min(delay + random.random() * base_delay, 60.0)
            return RetryDecision(RetryDecisionEnum.RETRY, total_delay)
        if status is not None:
            if status in RETRYABLE_STATUS:
                if method.upper() in IDEMPOTENT or allow_non_idempotent:
                    delay = base_delay * (2 ** (attempt - 1))
                    # Cap delay at 60 seconds to prevent excessive waits
                    total_delay = min(delay + random.random() * base_delay, 60.0)
                    return RetryDecision(RetryDecisionEnum.RETRY, total_delay)
        return RetryDecision(RetryDecisionEnum.GIVE_UP, None)

    return _strategy
