"""NexusClient and AsyncNexusClient — entry points for the SDK."""

from __future__ import annotations

from typing import Any

import httpx

from ._exceptions import raise_for_response
from .resources import (
    AsyncBalancesResource,
    AsyncBaaSResource,
    AsyncPaymentMethodsResource,
    AsyncSessionsResource,
    AsyncTransactionIntentsResource,
    BalancesResource,
    BaaSResource,
    PaymentMethodsResource,
    SessionsResource,
    TransactionIntentsResource,
)

# ---------------------------------------------------------------------------
# Base URLs
# ---------------------------------------------------------------------------

_GATEWAY_SANDBOX = "https://api.dev.neero.io/payment-gateway/api/v1"
_GATEWAY_LIVE = "https://api.neero.tech/payment-gateway/api/v1"
_BAAS_SANDBOX = "https://api.dev.neero.io/baas-gateway/api/v1"
_BAAS_LIVE = "https://api.neero.tech/baas-gateway/api/v1"

_DEFAULT_TIMEOUT = 30.0


# ---------------------------------------------------------------------------
# Sync client
# ---------------------------------------------------------------------------

class NexusClient:
    """Synchronous Nexus / Neero API client.

    Usage::

        with NexusClient(secret_key="sk_...", platform_code="MYAPP") as client:
            pm = client.payment_methods.create_mobile_money(
                "+237691111111", "CM", MobileMoneyProvider.ORANGE_MONEY
            )
            intent = client.intents.cash_in(
                source_payment_method_id=pm.id,
                destination_payment_method_id=merchant_pm_id,
                amount=5000,
            )
    """

    def __init__(
        self,
        secret_key: str,
        platform_code: str,
        *,
        sandbox: bool = True,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self.platform_code = platform_code
        self._sandbox = sandbox

        self._http = httpx.Client(
            auth=(secret_key, ""),
            base_url=_GATEWAY_SANDBOX if sandbox else _GATEWAY_LIVE,
            timeout=timeout,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        self._baas_http = httpx.Client(
            auth=(secret_key, ""),
            base_url=_BAAS_SANDBOX if sandbox else _BAAS_LIVE,
            timeout=timeout,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

        self.payment_methods = PaymentMethodsResource(self)
        self.intents = TransactionIntentsResource(self)
        self.balances = BalancesResource(self)
        self.sessions = SessionsResource(self)
        self.baas = BaaSResource(self)

    # ------------------------------------------------------------------
    # Internal HTTP helpers
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        idempotency_key: str | None = None,
        baas: bool = False,
        **kwargs: Any,
    ) -> dict:
        http = self._baas_http if baas else self._http
        headers: dict[str, str] = {}
        if idempotency_key:
            headers["X-IDEMPOTENCY-KEY"] = idempotency_key

        response = http.request(method, path, headers=headers, **kwargs)

        if not response.is_success:
            try:
                body = response.json()
            except Exception:
                body = {"code": "PARSE_ERROR", "message": response.text}
            raise_for_response(body, response.status_code)

        if response.status_code == 204 or not response.content:
            return {}
        return response.json()

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def close(self) -> None:
        self._http.close()
        self._baas_http.close()

    def __enter__(self) -> NexusClient:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()


# ---------------------------------------------------------------------------
# Async client
# ---------------------------------------------------------------------------

class AsyncNexusClient:
    """Async Nexus / Neero API client (httpx AsyncClient, awaitable methods).

    Usage::

        async with AsyncNexusClient(secret_key="sk_...", platform_code="MYAPP") as client:
            pm = await client.payment_methods.create_mobile_money(
                "+237691111111", "CM", MobileMoneyProvider.MTN_MONEY
            )
            intent = await client.intents.cash_in(
                source_payment_method_id=pm.id,
                destination_payment_method_id=merchant_pm_id,
                amount=5000,
            )
    """

    def __init__(
        self,
        secret_key: str,
        platform_code: str,
        *,
        sandbox: bool = True,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self.platform_code = platform_code
        self._sandbox = sandbox

        self._http = httpx.AsyncClient(
            auth=(secret_key, ""),
            base_url=_GATEWAY_SANDBOX if sandbox else _GATEWAY_LIVE,
            timeout=timeout,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        self._baas_http = httpx.AsyncClient(
            auth=(secret_key, ""),
            base_url=_BAAS_SANDBOX if sandbox else _BAAS_LIVE,
            timeout=timeout,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

        self.payment_methods = AsyncPaymentMethodsResource(self)
        self.intents = AsyncTransactionIntentsResource(self)
        self.balances = AsyncBalancesResource(self)
        self.sessions = AsyncSessionsResource(self)
        self.baas = AsyncBaaSResource(self)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        idempotency_key: str | None = None,
        baas: bool = False,
        **kwargs: Any,
    ) -> dict:
        http = self._baas_http if baas else self._http
        headers: dict[str, str] = {}
        if idempotency_key:
            headers["X-IDEMPOTENCY-KEY"] = idempotency_key

        response = await http.request(method, path, headers=headers, **kwargs)

        if not response.is_success:
            try:
                body = response.json()
            except Exception:
                body = {"code": "PARSE_ERROR", "message": response.text}
            raise_for_response(body, response.status_code)

        if response.status_code == 204 or not response.content:
            return {}
        return response.json()

    async def aclose(self) -> None:
        await self._http.aclose()
        await self._baas_http.aclose()

    async def __aenter__(self) -> AsyncNexusClient:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.aclose()
