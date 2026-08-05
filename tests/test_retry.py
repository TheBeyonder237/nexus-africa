"""Tests for the retry policy — pure helpers and the client retry loop."""

import httpx
import pytest
import respx

from nexus_africa import AsyncNexusClient, NexusClient
from nexus_africa._exceptions import PaymentMethodError, ServerError
from nexus_africa._retry import compute_backoff, is_retryable_status, parse_retry_after

GATEWAY = "https://api.dev.neero.io/payment-gateway/api/v1"
PM = {"id": "pm_1", "type": "MOBILE_MONEY"}


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("status,expected", [
    (429, True), (500, True), (502, True), (503, True), (504, True),
    (200, False), (400, False), (401, False), (404, False), (409, False),
])
def test_is_retryable_status(status, expected):
    assert is_retryable_status(status) is expected


@pytest.mark.parametrize("value,expected", [
    ("5", 5.0), ("0", 0.0), ("2.5", 2.5),
    (None, None), ("", None), ("soon", None), ("-1", None),
])
def test_parse_retry_after(value, expected):
    assert parse_retry_after(value) == expected


def test_compute_backoff_zero_factor_is_zero():
    assert compute_backoff(0, 0.0) == 0.0
    assert compute_backoff(5, 0.0) == 0.0


def test_compute_backoff_grows_within_jitter_bounds():
    # base = factor * 2**attempt; full jitter keeps result in [base, 2*base].
    for attempt in range(4):
        base = 0.5 * (2**attempt)
        delay = compute_backoff(attempt, 0.5)
        assert base <= delay <= 2 * base


def test_compute_backoff_honours_retry_after():
    assert compute_backoff(3, 0.5, retry_after=7.0) == 7.0


# ---------------------------------------------------------------------------
# Sync retry loop (backoff_factor=0 → no real sleeping)
# ---------------------------------------------------------------------------

def _client(max_retries=3):
    return NexusClient(
        "sk_test", platform_code="TEST", sandbox=True,
        max_retries=max_retries, backoff_factor=0.0,
    )


def test_retries_on_503_then_succeeds():
    with _client() as client, respx.mock:
        route = respx.get(f"{GATEWAY}/payment-methods/pm_1").mock(
            side_effect=[httpx.Response(503), httpx.Response(200, json=PM)]
        )
        pm = client.payment_methods.get("pm_1")
    assert pm.id == "pm_1"
    assert route.call_count == 2


def test_retries_on_429_then_succeeds():
    with _client() as client, respx.mock:
        route = respx.get(f"{GATEWAY}/payment-methods/pm_1").mock(
            side_effect=[httpx.Response(429), httpx.Response(200, json=PM)]
        )
        client.payment_methods.get("pm_1")
    assert route.call_count == 2


def test_retries_on_transport_error_then_succeeds():
    with _client() as client, respx.mock:
        route = respx.get(f"{GATEWAY}/payment-methods/pm_1").mock(
            side_effect=[httpx.ConnectError("boom"), httpx.Response(200, json=PM)]
        )
        client.payment_methods.get("pm_1")
    assert route.call_count == 2


def test_gives_up_after_max_retries():
    with _client(max_retries=2) as client, respx.mock:
        route = respx.get(f"{GATEWAY}/payment-methods/pm_1").mock(
            return_value=httpx.Response(500, json={"code": "SERVER_ERROR", "message": "boom"})
        )
        with pytest.raises(ServerError):
            client.payment_methods.get("pm_1")
    assert route.call_count == 3  # 1 initial + 2 retries


def test_does_not_retry_non_retryable_status():
    with _client() as client, respx.mock:
        route = respx.get(f"{GATEWAY}/payment-methods/pm_1").mock(
            return_value=httpx.Response(400, json={"code": "PM-0010", "message": "bad"})
        )
        with pytest.raises(PaymentMethodError):
            client.payment_methods.get("pm_1")
    assert route.call_count == 1


def test_max_retries_zero_disables_retrying():
    with _client(max_retries=0) as client, respx.mock:
        route = respx.get(f"{GATEWAY}/payment-methods/pm_1").mock(
            return_value=httpx.Response(503, json={"code": "SERVER_ERROR", "message": "down"})
        )
        with pytest.raises(ServerError):
            client.payment_methods.get("pm_1")
    assert route.call_count == 1


# ---------------------------------------------------------------------------
# Async retry loop
# ---------------------------------------------------------------------------

async def test_async_retries_on_503_then_succeeds():
    async with AsyncNexusClient(
        "sk_test", platform_code="TEST", sandbox=True, max_retries=3, backoff_factor=0.0
    ) as client:
        with respx.mock:
            route = respx.get(f"{GATEWAY}/payment-methods/pm_1").mock(
                side_effect=[httpx.Response(503), httpx.Response(200, json=PM)]
            )
            pm = await client.payment_methods.get("pm_1")
    assert pm.id == "pm_1"
    assert route.call_count == 2
