"""BaaS — Config (nationalities, required documents)."""

from __future__ import annotations

from ..._models import Nationality, RequiredDocument
from .._base import AsyncResource, SyncResource


class BaaSConfigResource(SyncResource):
    """Reference data for onboarding (nationalities, required documents)."""

    def list_nationalities(self) -> list[Nationality]:
        """List the nationalities accepted for KYC onboarding."""
        raw = self._get("/nationalities")
        # Endpoint may return a bare list or a ``{"data": [...]}`` envelope.
        items = raw if isinstance(raw, list) else raw.get("data", [])
        return [Nationality.model_validate(n) for n in items]

    def list_required_documents(self) -> list[RequiredDocument]:
        """List the KYC documents required to onboard a party."""
        raw = self._get("/required-documents")
        items = raw if isinstance(raw, list) else raw.get("data", [])
        return [RequiredDocument.model_validate(d) for d in items]


class AsyncBaaSConfigResource(AsyncResource):
    """Async variant of :class:`BaaSConfigResource`."""

    async def list_nationalities(self) -> list[Nationality]:
        raw = await self._get("/nationalities")
        items = raw if isinstance(raw, list) else raw.get("data", [])
        return [Nationality.model_validate(n) for n in items]

    async def list_required_documents(self) -> list[RequiredDocument]:
        raw = await self._get("/required-documents")
        items = raw if isinstance(raw, list) else raw.get("data", [])
        return [RequiredDocument.model_validate(d) for d in items]
