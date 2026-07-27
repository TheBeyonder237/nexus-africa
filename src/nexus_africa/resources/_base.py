"""Base resource — thin wrapper delegating HTTP to the client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .._client import AsyncNexusClient, NexusClient


class SyncResource:
    def __init__(self, client: NexusClient) -> None:
        self._client = client

    def _get(self, path: str, **params: Any) -> dict:
        return self._client._request("GET", path, params=params or None)

    def _post(self, path: str, body: dict | None = None, *, idempotency_key: str | None = None) -> dict:
        return self._client._request("POST", path, json=body, idempotency_key=idempotency_key)

    def _patch(self, path: str, body: dict | None = None) -> dict:
        return self._client._request("PATCH", path, json=body)

    def _put(self, path: str, body: dict | None = None) -> dict:
        return self._client._request("PUT", path, json=body)

    def _delete(self, path: str) -> dict:
        return self._client._request("DELETE", path)


class AsyncResource:
    def __init__(self, client: AsyncNexusClient) -> None:
        self._client = client

    async def _get(self, path: str, **params: Any) -> dict:
        return await self._client._request("GET", path, params=params or None)

    async def _post(self, path: str, body: dict | None = None, *, idempotency_key: str | None = None) -> dict:
        return await self._client._request("POST", path, json=body, idempotency_key=idempotency_key)

    async def _patch(self, path: str, body: dict | None = None) -> dict:
        return await self._client._request("PATCH", path, json=body)

    async def _put(self, path: str, body: dict | None = None) -> dict:
        return await self._client._request("PUT", path, json=body)

    async def _delete(self, path: str) -> dict:
        return await self._client._request("DELETE", path)
