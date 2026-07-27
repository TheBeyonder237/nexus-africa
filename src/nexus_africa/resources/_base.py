"""Base resource — thin wrapper delegating HTTP to the client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .._client import AsyncNexusClient, NexusClient


class SyncResource:
    """Base for synchronous resources.

    Resources hold no HTTP state of their own — every verb helper delegates to
    ``client._request`` so that base-URL selection, auth, idempotency and error
    handling live in one place. Subclasses just translate methods into paths.
    """

    def __init__(self, client: NexusClient) -> None:
        self._client = client

    def _get(self, path: str, **params: Any) -> dict[str, Any]:
        """GET ``path`` with optional query ``params`` (``None`` values dropped upstream)."""
        return self._client._request("GET", path, params=params or None)

    def _post(
        self, path: str, body: dict[str, Any] | None = None, *, idempotency_key: str | None = None
    ) -> dict[str, Any]:
        """POST ``body`` as JSON, optionally carrying an idempotency key."""
        return self._client._request("POST", path, json=body, idempotency_key=idempotency_key)

    def _patch(self, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        """PATCH ``path`` with an optional JSON ``body``."""
        return self._client._request("PATCH", path, json=body)

    def _put(self, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        """PUT ``path`` with an optional JSON ``body``."""
        return self._client._request("PUT", path, json=body)

    def _delete(self, path: str) -> dict[str, Any]:
        """DELETE ``path``."""
        return self._client._request("DELETE", path)


class AsyncResource:
    """Async base resource — awaitable mirror of :class:`SyncResource`."""

    def __init__(self, client: AsyncNexusClient) -> None:
        self._client = client

    async def _get(self, path: str, **params: Any) -> dict[str, Any]:
        """GET ``path`` with optional query ``params``."""
        return await self._client._request("GET", path, params=params or None)

    async def _post(
        self, path: str, body: dict[str, Any] | None = None, *, idempotency_key: str | None = None
    ) -> dict[str, Any]:
        """POST ``body`` as JSON, optionally carrying an idempotency key."""
        return await self._client._request("POST", path, json=body, idempotency_key=idempotency_key)

    async def _patch(self, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        """PATCH ``path`` with an optional JSON ``body``."""
        return await self._client._request("PATCH", path, json=body)

    async def _put(self, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        """PUT ``path`` with an optional JSON ``body``."""
        return await self._client._request("PUT", path, json=body)

    async def _delete(self, path: str) -> dict[str, Any]:
        """DELETE ``path``."""
        return await self._client._request("DELETE", path)
