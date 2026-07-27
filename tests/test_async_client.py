"""Async client smoke tests."""

import httpx
import pytest
import respx

from nexus_africa import AsyncNexusClient, MobileMoneyProvider, TransactionStatus

GATEWAY = "https://api.dev.neero.io/payment-gateway/api/v1"

PM_RESPONSE = {
    "id": "pm_async",
    "type": "MOBILE_MONEY",
    "mobileMoneyDetails": {
        "phoneNumber": "+237651111111",
        "countryIso": "CM",
        "mobileMoneyProvider": "MTN_MONEY",
    },
}

INTENT_RESPONSE = {
    "id": "intent_async",
    "status": "PENDING",
    "amount": 3000,
    "paymentType": "MERCHANT_COLLECTION",
    "sourcePaymentMethodId": "pm_async",
    "destinationPaymentMethodId": "pm_merchant",
    "platformCode": "TEST",
}


@pytest.mark.asyncio
async def test_async_create_mobile_money():
    async with AsyncNexusClient("sk_test", platform_code="TEST", sandbox=True) as client:
        with respx.mock:
            respx.post(f"{GATEWAY}/payment-methods").mock(
                return_value=httpx.Response(200, json=PM_RESPONSE)
            )
            pm = await client.payment_methods.create_mobile_money(
                "+237651111111", "CM", MobileMoneyProvider.MTN_MONEY
            )
    assert pm.id == "pm_async"


@pytest.mark.asyncio
async def test_async_cash_in():
    async with AsyncNexusClient("sk_test", platform_code="TEST", sandbox=True) as client:
        with respx.mock:
            respx.post(f"{GATEWAY}/transaction-intents/cash-in").mock(
                return_value=httpx.Response(200, json=INTENT_RESPONSE)
            )
            intent = await client.intents.cash_in(
                source_payment_method_id="pm_async",
                destination_payment_method_id="pm_merchant",
                amount=3000,
            )
    assert intent.status == TransactionStatus.PENDING
    assert intent.amount == 3000


@pytest.mark.asyncio
async def test_async_context_manager():
    """AsyncNexusClient should support async with."""
    async with AsyncNexusClient("sk_test", platform_code="TEST") as client:
        assert client.platform_code == "TEST"
