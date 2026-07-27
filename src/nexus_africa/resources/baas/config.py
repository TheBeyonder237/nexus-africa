"""BaaS — Config (nationalities, required documents)."""

from __future__ import annotations

from ..._models import Nationality, RequiredDocument
from .._base import AsyncResource, SyncResource


class BaaSConfigResource(SyncResource):
    def list_nationalities(self) -> list[Nationality]:
        raw = self._get("/nationalities")
        items = raw if isinstance(raw, list) else raw.get("data", [])
        return [Nationality.model_validate(n) for n in items]

    def list_required_documents(self) -> list[RequiredDocument]:
        raw = self._get("/required-documents")
        items = raw if isinstance(raw, list) else raw.get("data", [])
        return [RequiredDocument.model_validate(d) for d in items]


class AsyncBaaSConfigResource(AsyncResource):
    async def list_nationalities(self) -> list[Nationality]:
        raw = await self._get("/nationalities")
        items = raw if isinstance(raw, list) else raw.get("data", [])
        return [Nationality.model_validate(n) for n in items]

    async def list_required_documents(self) -> list[RequiredDocument]:
        raw = await self._get("/required-documents")
        items = raw if isinstance(raw, list) else raw.get("data", [])
        return [RequiredDocument.model_validate(d) for d in items]
