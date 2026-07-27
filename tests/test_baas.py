"""Tests for BaaS resources — focus on base-URL routing (mocked HTTP).

The regression these guard against: BaaS resources used to call the client
without the ``baas`` flag and therefore hit the payment-gateway host instead
of ``/baas-gateway``. Each test mocks **only** the BaaS host, so a request
wrongly routed to the gateway raises an unmocked-request error and fails.
"""

import httpx
import pytest
import respx

from nexus_africa import AsyncNexusClient, NexusClient

GATEWAY = "https://api.dev.neero.io/payment-gateway/api/v1"
BAAS = "https://api.dev.neero.io/baas-gateway/api/v1"


@pytest.fixture
def client():
    with NexusClient("sk_test", platform_code="TEST", sandbox=True) as c:
        yield c


# ---------------------------------------------------------------------------
# Sync routing
# ---------------------------------------------------------------------------

def test_list_nationalities_hits_baas_host(client):
    with respx.mock:
        route = respx.get(f"{BAAS}/nationalities").mock(
            return_value=httpx.Response(200, json={"data": [{"code": "CM", "name": "Cameroon"}]})
        )
        nationalities = client.baas.config.list_nationalities()

    assert route.called
    assert route.calls.last.request.url.host == "api.dev.neero.io"
    assert "/baas-gateway/" in str(route.calls.last.request.url)
    assert nationalities[0].code == "CM"


def test_create_virtual_card_hits_baas_host(client):
    with respx.mock:
        route = respx.post(f"{BAAS}/cards").mock(
            return_value=httpx.Response(200, json={"id": 42, "category": "VIRTUAL"})
        )
        card = client.baas.cards.create_virtual(party_id="party_1")

    assert route.called
    assert "/baas-gateway/" in str(route.calls.last.request.url)
    assert card.id == 42


def test_get_party_hits_baas_host(client):
    with respx.mock:
        route = respx.get(f"{BAAS}/parties/party_1").mock(
            return_value=httpx.Response(200, json={"id": "party_1", "status": "ACTIVE"})
        )
        party = client.baas.parties.get("party_1")

    assert route.called
    assert party.id == "party_1"


def test_baas_call_does_not_reach_gateway(client):
    """A BaaS call must not match a gateway route with the same path."""
    with respx.mock:
        gateway_route = respx.get(f"{GATEWAY}/nationalities").mock(
            return_value=httpx.Response(200, json={"data": []})
        )
        baas_route = respx.get(f"{BAAS}/nationalities").mock(
            return_value=httpx.Response(200, json={"data": [{"code": "CM"}]})
        )
        client.baas.config.list_nationalities()

    assert baas_route.called
    assert not gateway_route.called


# ---------------------------------------------------------------------------
# Async routing
# ---------------------------------------------------------------------------

async def test_async_onboarding_hits_baas_host():
    async with AsyncNexusClient("sk_test", platform_code="TEST", sandbox=True) as client:
        with respx.mock:
            route = respx.post(f"{BAAS}/onboarding-sessions").mock(
                return_value=httpx.Response(200, json={"id": "sess_1", "status": "PENDING"})
            )
            session = await client.baas.onboarding.create_session(nationality_code="CM")

    assert route.called
    assert "/baas-gateway/" in str(route.calls.last.request.url)
    assert session.id == "sess_1"
