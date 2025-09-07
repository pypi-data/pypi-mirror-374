import asyncio
import time
from collections.abc import Awaitable
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from typing import Callable, Optional, TypeVar

import httpx

_T = TypeVar("_T")


@dataclass(frozen=True)
class RetryConfig:
    """
    Configuration for retry behavior.

    Backoff uses exponential growth:
        delay = backoff_base * (backoff_factor ** (attempt-1)) + jitter

    Jitter strategy: "equal jitter" (uniform random in [jitter[0], jitter[1]]).
    """

    enabled: bool = True
    max_attempts: int = 5
    backoff_base: float = 0.5
    backoff_factor: float = 2.0
    jitter: tuple[float, float] = (0.1, 0.3)
    # Include 408, 429, 500, 502, 503, 504 by default; 503 already present
    retry_on_status: tuple[int, ...] = (408, 429, 500, 502, 503, 504)
    # Transport + timeout errors (Connect/Read/Write/Pool timeouts derive from TimeoutException)
    retry_on_exceptions: tuple[type, ...] = (
        httpx.TransportError,
        httpx.TimeoutException,
    )
    # How many seconds before credential expiry we proactively refresh (ADC)
    adc_clock_skew: float = 60.0


async def with_retries(
    func: Callable[[], Awaitable[_T]],
    retry_conf: RetryConfig,
    classify: Callable[[Optional[httpx.Response], Optional[BaseException]], bool],
    *,
    delay_override: Optional[
        Callable[[Optional[httpx.Response], Optional[BaseException]], Optional[float]]
    ] = None,
    sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
    rng: Optional[Callable[[float, float], float]] = None,
) -> _T:
    """
    Generic async retry loop. Calls `func` up to `max_attempts`.
    `classify` decides if we should retry based on response/exception.
    `delay_override` (e.g., Retry-After) can override the exponential backoff delay.
    """
    import random

    if rng is None:
        rng = random.uniform

    attempt = 1
    while True:
        try:
            return await func()
        except asyncio.CancelledError:
            # Do not retry on cancellation
            raise
        except KeyboardInterrupt:
            # Bubble up promptly
            raise
        except Exception as exc:  # noqa: BLE001
            resp = getattr(exc, "response", None)
            should_retry = retry_conf.enabled and (
                isinstance(exc, retry_conf.retry_on_exceptions) or classify(resp, exc)
            )
            if not should_retry or attempt >= retry_conf.max_attempts:
                raise

            # Compute delay: Retry-After (if provided) else exponential + jitter
            if delay_override:
                override = delay_override(resp, exc)
            else:
                override = None

            if override is not None:
                delay = float(override)
            else:
                delay = retry_conf.backoff_base * (
                    retry_conf.backoff_factor ** (attempt - 1)
                )
                low, high = retry_conf.jitter
                delay += rng(low, high) if high > 0 else 0.0

            await sleeper(delay)
            attempt += 1


def _parse_retry_after_seconds(
    value: str, *, now_ts: Optional[float] = None
) -> Optional[float]:
    """Parse a Retry-After value (seconds or HTTP-date) into a delay in seconds."""
    if not value:
        return None
    value = value.strip()
    if value.isdigit():
        return float(value)
    try:
        dt = parsedate_to_datetime(value)
        # HTTP-date is always GMT; convert to POSIX seconds
        target_ts = dt.timestamp()
        curr = now_ts if now_ts is not None else time.time()
        delay = max(0.0, target_ts - curr)
        return delay
    except Exception:
        return None


def default_retry_classifier(
    retry_conf: RetryConfig,
) -> Callable[[Optional[httpx.Response], Optional[BaseException]], bool]:
    """
    Return a classifier that retries on configured statuses.
    Transport/timeout exceptions are handled separately by isinstance checks.
    """

    def _classifier(
        resp: Optional[httpx.Response], exc: Optional[BaseException]
    ) -> bool:
        if resp is not None and resp.status_code in retry_conf.retry_on_status:
            return True
        return False

    return _classifier


def default_retry_delay_override(
    resp: Optional[httpx.Response],
    exc: Optional[BaseException],
) -> Optional[float]:
    """
    If the response provides a Retry-After header, return its delay (seconds)
    to override the exponential backoff for this attempt; otherwise None.
    """
    if resp is None:
        return None
    ra = resp.headers.get("Retry-After")
    if not ra:
        return None
    return _parse_retry_after_seconds(ra)
