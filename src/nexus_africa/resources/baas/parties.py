"""BaaS — Party (KYC-validated identities)."""

from __future__ import annotations

from ..._models import Party
from .._base import AsyncBaaSBase, SyncBaaSBase


class BaaSPartiesResource(SyncBaaSBase):
    """Look up KYC-validated parties."""

    def get(self, party_id: str) -> Party:
        """Retrieve a single Party by id."""
        raw = self._get(f"/parties/{party_id}")
        return Party.model_validate(raw)

    def get_active(self) -> Party:
        """Return the currently active (linked) Party for this account."""
        raw = self._get("/parties/active")
        return Party.model_validate(raw)

    def list(self) -> list[Party]:
        """List all parties linked to this account."""
        raw = self._get("/parties")
        items = raw if isinstance(raw, list) else raw.get("data", [])
        return [Party.model_validate(p) for p in items]


class AsyncBaaSPartiesResource(AsyncBaaSBase):
    """Async variant of :class:`BaaSPartiesResource`."""

    async def get(self, party_id: str) -> Party:
        raw = await self._get(f"/parties/{party_id}")
        return Party.model_validate(raw)

    async def get_active(self) -> Party:
        raw = await self._get("/parties/active")
        return Party.model_validate(raw)

    async def list(self) -> list[Party]:
        raw = await self._get("/parties")
        items = raw if isinstance(raw, list) else raw.get("data", [])
        return [Party.model_validate(p) for p in items]
