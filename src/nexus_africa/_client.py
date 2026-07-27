"""NexusClient and AsyncNexusClient — entry points for the SDK."""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from ._exceptions import raise_for_response
from ._retry import compute_backoff, is_retryable_status, parse_retry_after
from .resources import (
    AsyncBaaSResource,
    AsyncBalancesResource,
    AsyncPaymentMethodsResource,
    AsyncSessionsResource,
    AsyncTransactionIntentsResource,
    BaaSResource,
    BalancesResource,
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
_DEFAULT_MAX_RETRIES = 3
_DEFAULT_BACKOFF_FACTOR = 0.5


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
        max_retries: int = _DEFAULT_MAX_RETRIES,
        backoff_factor: float = _DEFAULT_BACKOFF_FACTOR,
    ) -> None:
        """Build a client and its two httpx sessions (gateway + BaaS).

        Args:
            secret_key:     Nexus secret key; sent as HTTP Basic auth username
                            with an empty password.
            platform_code:  Mandatory COBAC/ANIF platform code, propagated to
                            transaction intents that don't override it.
            sandbox:        Target the sandbox (default) or live base URLs.
            timeout:        Per-request timeout in seconds.
            max_retries:    Extra attempts on transient failures (429, 5xx,
                            transport errors). ``0`` disables retrying.
            backoff_factor: Base for exponential backoff, in seconds; the
                            wait before a retry is ``backoff_factor * 2**n``
                            with jitter, unless a ``Retry-After`` header applies.
        """
        self.platform_code = platform_code
        self._sandbox = sandbox
        self._max_retries = max_retries
        self._backoff_factor = backoff_factor

        # Two sessions: one per base URL. _request routes to the right one via
        # its ``baas`` flag; both share the same Basic-auth credentials.
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
    ) -> dict[str, Any]:
        """Send a request and return the decoded JSON body.

        Args:
            method:          HTTP verb.
            path:            Path relative to the selected base URL.
            idempotency_key: Sent as ``X-IDEMPOTENCY-KEY`` on writes.
            baas:            Route to the BaaS base URL instead of the gateway.
            **kwargs:        Forwarded to httpx (``json``, ``params``, ...).

        Transient failures (429, 5xx, transport errors) are retried up to
        ``max_retries`` times with exponential backoff; other errors raise
        immediately.

        Returns:
            The parsed JSON object, or ``{}`` for 204 / empty responses.

        Raises:
            NexusError: For any non-2xx response (see :func:`raise_for_response`).
        """
        http = self._baas_http if baas else self._http
        headers: dict[str, str] = {}
        if idempotency_key:
            headers["X-IDEMPOTENCY-KEY"] = idempotency_key

        for attempt in range(self._max_retries + 1):
            can_retry = attempt < self._max_retries
            try:
                response = http.request(method, path, headers=headers, **kwargs)
            except httpx.TransportError:
                # Connection/timeout error: retry if attempts remain, else propagate.
                if not can_retry:
                    raise
                time.sleep(compute_backoff(attempt, self._backoff_factor))
                continue

            if response.is_success:
                if response.status_code == 204 or not response.content:
                    return {}
                data: dict[str, Any] = response.json()
                return data

            if can_retry and is_retryable_status(response.status_code):
                retry_after = parse_retry_after(response.headers.get("Retry-After"))
                time.sleep(compute_backoff(attempt, self._backoff_factor, retry_after=retry_after))
                continue

            # Non-retryable status, or retries exhausted: raise the typed error.
            try:
                body = response.json()
            except Exception:
                body = {"code": "PARSE_ERROR", "message": response.text}
            raise_for_response(body, response.status_code)

        raise RuntimeError("unreachable: retry loop exited without returning")  # pragma: no cover

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
        max_retries: int = _DEFAULT_MAX_RETRIES,
        backoff_factor: float = _DEFAULT_BACKOFF_FACTOR,
    ) -> None:
        """Build an async client. See :class:`NexusClient` for the arguments."""
        self.platform_code = platform_code
        self._sandbox = sandbox
        self._max_retries = max_retries
        self._backoff_factor = backoff_factor

        # Two async sessions mirroring the sync client (gateway + BaaS).
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
    ) -> dict[str, Any]:
        """Async counterpart of :meth:`NexusClient._request`."""
        http = self._baas_http if baas else self._http
        headers: dict[str, str] = {}
        if idempotency_key:
            headers["X-IDEMPOTENCY-KEY"] = idempotency_key

        for attempt in range(self._max_retries + 1):
            can_retry = attempt < self._max_retries
            try:
                response = await http.request(method, path, headers=headers, **kwargs)
            except httpx.TransportError:
                # Connection/timeout error: retry if attempts remain, else propagate.
                if not can_retry:
                    raise
                await asyncio.sleep(compute_backoff(attempt, self._backoff_factor))
                continue

            if response.is_success:
                if response.status_code == 204 or not response.content:
                    return {}
                data: dict[str, Any] = response.json()
                return data

            if can_retry and is_retryable_status(response.status_code):
                retry_after = parse_retry_after(response.headers.get("Retry-After"))
                await asyncio.sleep(
                    compute_backoff(attempt, self._backoff_factor, retry_after=retry_after)
                )
                continue

            # Non-retryable status, or retries exhausted: raise the typed error.
            try:
                body = response.json()
            except Exception:
                body = {"code": "PARSE_ERROR", "message": response.text}
            raise_for_response(body, response.status_code)

        raise RuntimeError("unreachable: retry loop exited without returning")  # pragma: no cover

    async def aclose(self) -> None:
        await self._http.aclose()
        await self._baas_http.aclose()

    async def __aenter__(self) -> AsyncNexusClient:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.aclose()
