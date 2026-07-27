"""pytest fixtures shared across all tests."""

import pytest
import respx
import httpx

SANDBOX_GATEWAY = "https://api.dev.neero.io/payment-gateway/api/v1"
SANDBOX_BAAS = "https://api.dev.neero.io/baas-gateway/api/v1"

TEST_SECRET = "test_secret_key"
TEST_PLATFORM = "TESTAPP"


@pytest.fixture
def gateway_mock():
    """Mock the Nexus gateway base URL."""
    with respx.mock(base_url=SANDBOX_GATEWAY, assert_all_called=False) as mock:
        yield mock


@pytest.fixture
def sync_client():
    from nexus_africa import NexusClient
    with NexusClient(TEST_SECRET, platform_code=TEST_PLATFORM, sandbox=True) as c:
        yield c


@pytest.fixture
async def async_client():
    from nexus_africa import AsyncNexusClient
    async with AsyncNexusClient(TEST_SECRET, platform_code=TEST_PLATFORM, sandbox=True) as c:
        yield c
