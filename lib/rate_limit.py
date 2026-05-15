"""Rate-limit detection and backoff for YouTube ingest."""
from __future__ import annotations

import random
import re
import time
from typing import Callable, TypeVar

T = TypeVar("T")

BLOCK_PATTERNS = re.compile(
    r"429|too many requests|rate limit|sign in to confirm|"
    r"ip blocked|blocked|unusual traffic|bot detection|"
    r"http error 403|forbidden",
    re.I,
)


def is_rate_limit_error(exc: BaseException | str) -> bool:
    text = str(exc) if not isinstance(exc, str) else exc
    return bool(BLOCK_PATTERNS.search(text))


def sleep_with_jitter(base_seconds: float, jitter: float = 0.0) -> None:
    extra = random.uniform(0, jitter) if jitter > 0 else 0
    time.sleep(base_seconds + extra)


def retry_with_backoff(
    fn: Callable[[], T],
    *,
    max_retries: int = 4,
    base_seconds: float = 30.0,
    label: str = "request",
) -> T:
    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception as e:
            last_exc = e
            if not is_rate_limit_error(e) or attempt >= max_retries:
                raise
            wait = base_seconds * (2**attempt) + random.uniform(5, 20)
            time.sleep(wait)
    raise last_exc  # type: ignore[misc]
