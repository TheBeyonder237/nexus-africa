"""Tests for the TransactionIntents resource."""

import httpx
import pytest
import respx

from nexus_africa import NexusClient, TransactionStatus
from nexus_africa._exceptions import IdempotencyConflict, TransactionIntentError

GATEWAY = "https://api.dev.neero.io/payment-gateway/api/v1"

INTENT_RESPONSE = {
    "id": "intent_xyz789",
    "status": "PENDING",
    "amount": 5000,
    "paymentType": "MERCHANT_COLLECTION",
    "sourcePaymentMethodId": "pm_source",
    "destinationPaymentMethodId": "pm_dest",
    "platformCode": "TEST",
}


@pytest.fixture
def client():
    with NexusClient("sk_test", platform_code="TEST", sandbox=True) as c:
        yield c


def test_cash_in(client):
    with respx.mock:
        respx.post(f"{GATEWAY}/transaction-intents/cash-in").mock(
            return_value=httpx.Response(200, json=INTENT_RESPONSE)
        )
        intent = client.intents.cash_in(
            source_payment_method_id="pm_source",
            destination_payment_method_id="pm_dest",
            amount=5000,
        )
    assert intent.id == "intent_xyz789"
    assert intent.status == TransactionStatus.PENDING
    assert intent.amount == 5000


def test_cash_in_uses_client_platform_code(client):
    """platform_code should default to client.platform_code."""
    captured = {}

    def capture_request(request):
        import json
        captured["body"] = json.loads(request.content)
        return httpx.Response(200, json=INTENT_RESPONSE)

    with respx.mock:
        respx.post(f"{GATEWAY}/transaction-intents/cash-in").mock(side_effect=capture_request)
        client.intents.cash_in(
            source_payment_method_id="pm_source",
            destination_payment_method_id="pm_dest",
            amount=1000,
        )
    assert captured["body"]["platformCode"] == "TEST"


def test_cash_in_sends_currency_code(client):
    """currencyCode is required by the API; it must be in the body (default XAF)."""
    captured = {}

    def capture_request(request):
        import json
        captured["body"] = json.loads(request.content)
        return httpx.Response(200, json=INTENT_RESPONSE)

    with respx.mock:
        respx.post(f"{GATEWAY}/transaction-intents/cash-in").mock(side_effect=capture_request)
        client.intents.cash_in(
            source_payment_method_id="pm_source",
            destination_payment_method_id="pm_dest",
            amount=1000,
        )
        client.intents.cash_in(
            source_payment_method_id="pm_source",
            destination_payment_method_id="pm_dest",
            amount=1000,
            currency_code="EUR",
        )
    assert captured["body"]["currencyCode"] == "EUR"

    # And the default on the first call was XAF.
    captured.clear()
    with respx.mock:
        respx.post(f"{GATEWAY}/transaction-intents/cash-in").mock(side_effect=capture_request)
        client.intents.cash_in(
            source_payment_method_id="pm_source",
            destination_payment_method_id="pm_dest",
            amount=1000,
        )
    assert captured["body"]["currencyCode"] == "XAF"


def test_cash_out(client):
    response = {**INTENT_RESPONSE, "paymentType": "ORANGE_MONEY_TRANSFER"}
    with respx.mock:
        respx.post(f"{GATEWAY}/transaction-intents/cash-out").mock(
            return_value=httpx.Response(200, json=response)
        )
        from nexus_africa import PaymentType
        intent = client.intents.cash_out(
            source_payment_method_id="pm_dest",
            destination_payment_method_id="pm_source",
            amount=5000,
            payment_type=PaymentType.ORANGE_MONEY_TRANSFER,
        )
    assert intent.amount == 5000


def test_get_intent(client):
    with respx.mock:
        respx.get(f"{GATEWAY}/transaction-intents/intent_xyz789").mock(
            return_value=httpx.Response(200, json=INTENT_RESPONSE)
        )
        intent = client.intents.get("intent_xyz789")
    assert intent.id == "intent_xyz789"


def test_confirm(client):
    confirmed = {**INTENT_RESPONSE, "status": "SUCCESSFUL"}
    with respx.mock:
        respx.post(f"{GATEWAY}/transaction-intents/intent_xyz789/confirm").mock(
            return_value=httpx.Response(200, json=confirmed)
        )
        intent = client.intents.confirm("intent_xyz789")
    assert intent.status == TransactionStatus.SUCCESSFUL


def test_cancel(client):
    cancelled = {**INTENT_RESPONSE, "status": "CANCELLED"}
    with respx.mock:
        respx.patch(f"{GATEWAY}/transaction-intents/intent_xyz789/cancel").mock(
            return_value=httpx.Response(200, json=cancelled)
        )
        intent = client.intents.cancel("intent_xyz789")
    assert intent.status == TransactionStatus.CANCELLED


def test_idempotency_conflict(client):
    error_body = {
        "code": "GE-0002",
        "message": "Idempotency Key Already Exists",
        "status": "CONFLICT",
    }
    with respx.mock:
        respx.post(f"{GATEWAY}/transaction-intents/cash-in").mock(
            return_value=httpx.Response(409, json=error_body)
        )
        with pytest.raises(IdempotencyConflict):
            client.intents.cash_in(
                source_payment_method_id="pm_source",
                destination_payment_method_id="pm_dest",
                amount=5000,
                idempotency_key="dup_key",
            )


def test_missing_platform_code_error(client):
    error_body = {
        "code": "TI-0014",
        "message": "Platform Code Required",
        "status": "BAD_REQUEST",
    }
    with respx.mock:
        respx.post(f"{GATEWAY}/transaction-intents/cash-in").mock(
            return_value=httpx.Response(400, json=error_body)
        )
        with pytest.raises(TransactionIntentError) as exc:
            client.intents.cash_in(
                source_payment_method_id="pm_source",
                destination_payment_method_id="pm_dest",
                amount=5000,
                platform_code="",
            )
    assert exc.value.code == "TI-0014"
