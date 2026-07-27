"""Nexus webhook signature verification — HMAC-SHA512."""

from __future__ import annotations

import hashlib
import hmac
import json
import time

from ._models import WebhookEvent


def verify_signature(
    raw_body: bytes,
    timestamp: str,
    signature: str,
    secret: str,
) -> bool:
    """Return True if the webhook signature is valid.

    Nexus signs: HMAC-SHA512(secret, timestamp_str + raw_body_str)

    Args:
        raw_body:  The raw request body bytes, **before** any JSON parsing.
        timestamp: Value of the ``X-TIMESTAMP`` header.
        signature: Value of the ``X-SIGNATURE`` header.
        secret:    Your webhook signing secret from the Nexus dashboard.

    Important: pass the raw bytes received over the wire, never a
    re-serialised dict — any byte difference will break the check.
    """
    message = (timestamp + raw_body.decode("utf-8")).encode("utf-8")
    expected = hmac.new(secret.encode("utf-8"), message, hashlib.sha512).hexdigest()
    return hmac.compare_digest(signature, expected)


def parse_event(raw_body: bytes) -> WebhookEvent:
    """Deserialise a webhook body into a typed :class:`WebhookEvent`."""
    return WebhookEvent.model_validate(json.loads(raw_body))


def verify_and_parse(
    raw_body: bytes,
    timestamp: str,
    signature: str,
    secret: str,
    *,
    max_age_seconds: int = 300,
) -> WebhookEvent:
    """Verify signature + timestamp freshness, then parse event.

    Args:
        raw_body:         Raw request body bytes.
        timestamp:        ``X-TIMESTAMP`` header value (Unix epoch as string).
        signature:        ``X-SIGNATURE`` header value.
        secret:           Webhook signing secret.
        max_age_seconds:  Reject events older than this (replay protection).

    Raises:
        ValueError: On invalid signature or stale timestamp.
    """
    if not verify_signature(raw_body, timestamp, signature, secret):
        raise ValueError("Invalid webhook signature")

    try:
        event_time = int(timestamp)
    except ValueError:
        raise ValueError(f"Unparseable X-TIMESTAMP: {timestamp!r}")

    age = int(time.time()) - event_time
    if age > max_age_seconds:
        raise ValueError(f"Webhook timestamp is {age}s old (max {max_age_seconds}s)")

    return parse_event(raw_body)
