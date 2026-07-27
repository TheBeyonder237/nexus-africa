"""BaaS — Card issuance (virtual cards)."""

from __future__ import annotations

from typing import Any

from ..._enums import CardCategory
from ..._models import Card, CardSecureDetails, CardViewLink, CreateCardRequest
from .._base import AsyncResource, SyncResource


class BaaSCardsResource(SyncResource):
    def create_virtual(self, party_id: str) -> Card:
        """Issue a new virtual card for a KYC-validated Party."""
        req = CreateCardRequest(party_id=party_id, card_category=CardCategory.VIRTUAL)
        raw = self._post("/cards", req.model_dump(by_alias=True, exclude_none=True))
        return Card.model_validate(raw)

    def freeze(self, card_id: int) -> Card:
        """Freeze a card — blocks all transactions."""
        raw = self._put(f"/cards/{card_id}/freeze", {"frozen": True})
        return Card.model_validate(raw)

    def unfreeze(self, card_id: int) -> Card:
        """Unfreeze a previously frozen card."""
        raw = self._put(f"/cards/{card_id}/freeze", {"frozen": False})
        return Card.model_validate(raw)

    def get_view_link(self, card_id: int) -> CardViewLink:
        """Obtain a short-lived URL to display masked card details."""
        raw = self._post(f"/cards/{card_id}/view-link")
        return CardViewLink.model_validate(raw)

    def get_secure_details(self, card_id: int) -> CardSecureDetails:
        """Retrieve PCI-sensitive card details (PAN, CVV, expiry)."""
        raw = self._get(f"/cards/{card_id}/secure-details")
        return CardSecureDetails.model_validate(raw)

    def cancel(self, card_id: int) -> dict[str, Any]:
        """Permanently cancel (delete) a card."""
        return self._delete(f"/cards/{card_id}")


class AsyncBaaSCardsResource(AsyncResource):
    async def create_virtual(self, party_id: str) -> Card:
        req = CreateCardRequest(party_id=party_id, card_category=CardCategory.VIRTUAL)
        raw = await self._post("/cards", req.model_dump(by_alias=True, exclude_none=True))
        return Card.model_validate(raw)

    async def freeze(self, card_id: int) -> Card:
        raw = await self._put(f"/cards/{card_id}/freeze", {"frozen": True})
        return Card.model_validate(raw)

    async def unfreeze(self, card_id: int) -> Card:
        raw = await self._put(f"/cards/{card_id}/freeze", {"frozen": False})
        return Card.model_validate(raw)

    async def get_view_link(self, card_id: int) -> CardViewLink:
        raw = await self._post(f"/cards/{card_id}/view-link")
        return CardViewLink.model_validate(raw)

    async def get_secure_details(self, card_id: int) -> CardSecureDetails:
        raw = await self._get(f"/cards/{card_id}/secure-details")
        return CardSecureDetails.model_validate(raw)

    async def cancel(self, card_id: int) -> dict[str, Any]:
        return await self._delete(f"/cards/{card_id}")
