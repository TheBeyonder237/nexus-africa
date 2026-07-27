"""Integration-style tests for the PaymentMethods resource (mocked HTTP)."""

import httpx
import pytest
import respx

from nexus_africa import MobileMoneyProvider, NexusClient, PaymentMethodType
from nexus_africa._exceptions import PaymentMethodError

GATEWAY = "https://api.dev.neero.io/payment-gateway/api/v1"

PM_RESPONSE = {
    "id": "pm_abc123",
    "type": "MOBILE_MONEY",
    "mobileMoneyDetails": {
        "phoneNumber": "+237691111111",
        "countryIso": "CM",
        "mobileMoneyProvider": "ORANGE_MONEY",
    },
}


@pytest.fixture
def client():
    with NexusClient("sk_test", platform_code="TEST", sandbox=True) as c:
        yield c


def test_create_mobile_money(client):
    with respx.mock:
        respx.post(f"{GATEWAY}/payment-methods").mock(
            return_value=httpx.Response(200, json=PM_RESPONSE)
        )
        pm = client.payment_methods.create_mobile_money(
            "+237691111111", "CM", MobileMoneyProvider.ORANGE_MONEY
        )
    assert pm.id == "pm_abc123"
    assert pm.type == PaymentMethodType.MOBILE_MONEY
    assert pm.mobile_money_details.phone_number == "+237691111111"


def test_get_payment_method(client):
    with respx.mock:
        respx.get(f"{GATEWAY}/payment-methods/pm_abc123").mock(
            return_value=httpx.Response(200, json=PM_RESPONSE)
        )
        pm = client.payment_methods.get("pm_abc123")
    assert pm.id == "pm_abc123"


def test_list_payment_methods(client):
    with respx.mock:
        respx.get(f"{GATEWAY}/payment-methods").mock(
            return_value=httpx.Response(200, json={"data": [PM_RESPONSE]})
        )
        methods = client.payment_methods.list()
    assert len(methods) == 1
    assert methods[0].id == "pm_abc123"


def test_create_raises_pm_error(client):
    error_body = {
        "code": "PM-0010",
        "message": "Invalid Payment Method Details",
        "status": "BAD_REQUEST",
    }
    with respx.mock:
        respx.post(f"{GATEWAY}/payment-methods").mock(
            return_value=httpx.Response(400, json=error_body)
        )
        with pytest.raises(PaymentMethodError) as exc:
            client.payment_methods.create_mobile_money(
                "invalid", "CM", MobileMoneyProvider.ORANGE_MONEY
            )
    assert exc.value.code == "PM-0010"
