"""Balances resource."""

from __future__ import annotations

from .._models import Balance
from ._base import AsyncResource, SyncResource


class BalancesResource(SyncResource):
    def get(self, payment_method_id: str) -> Balance:
        """Retrieve the balance for a Nexus Merchant Payment Method."""
        raw = self._get(f"/balances/payment-method/{payment_method_id}")
        return Balance.model_validate(raw)


class AsyncBalancesResource(AsyncResource):
    async def get(self, payment_method_id: str) -> Balance:
        raw = await self._get(f"/balances/payment-method/{payment_method_id}")
        return Balance.model_validate(raw)
