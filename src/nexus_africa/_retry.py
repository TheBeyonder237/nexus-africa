"""Retry policy helpers — pure functions, no I/O.

The client retries transient failures (HTTP 429 and 5xx, plus transport-level
errors such as timeouts and connection resets) with exponential backoff and
full jitter. Everything here is side-effect free so it can be unit-tested and
reused by both the sync and async request loops; the actual sleeping happens
in the client.
"""

from __future__ import annotations

import random

#: Statuses worth retrying: rate limiting and server-side failures.
RETRYABLE_STATUSES: frozenset[int] = frozenset({429, 500, 502, 503, 504})


def is_retryable_status(status_code: int) -> bool:
    """Return True if a response with this status should be retried."""
    return status_code in RETRYABLE_STATUSES


def parse_retry_after(value: str | None) -> float | None:
    """Parse a ``Retry-After`` header expressed in seconds.

    Only the delta-seconds form is supported (the form Nexus uses). An
    HTTP-date value or anything unparseable yields ``None`` so the caller
    falls back to computed backoff.
    """
    if not value:
        return None
    try:
        seconds = float(value)
    except ValueError:
        return None
    return seconds if seconds >= 0 else None


def compute_backoff(
    attempt: int,
    backoff_factor: float,
    *,
    retry_after: float | None = None,
) -> float:
    """Seconds to wait before the retry following ``attempt`` (0-indexed).

    A server-provided ``retry_after`` always wins. Otherwise the delay is
    ``backoff_factor * 2**attempt`` with full jitter (a uniform value in
    ``[0, base]`` is added), which spreads retries out and avoids thundering
    herds. With ``backoff_factor == 0`` the delay is always ``0``.
    """
    if retry_after is not None:
        return retry_after
    base = backoff_factor * (2**attempt)
    return float(base + random.uniform(0, base))
