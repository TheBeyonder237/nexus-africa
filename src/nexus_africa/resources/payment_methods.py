"""Payment Methods resource."""

from __future__ import annotations

from typing import Any

from .._enums import MobileMoneyProvider, PaymentMethodType
from .._models import (
    CreatePaymentMethodRequest,
    MobileMoneyDetails,
    NexusMerchantDetails,
    PaymentMethod,
    PaymentMethodList,
)
from ._base import AsyncResource, SyncResource


def _mobile_money_request(
    phone_number: str,
    country_iso: str,
    provider: MobileMoneyProvider,
) -> CreatePaymentMethodRequest:
    return CreatePaymentMethodRequest(
        type=PaymentMethodType.MOBILE_MONEY,
        mobile_money_details=MobileMoneyDetails(
            phone_number=phone_number,
            country_iso=country_iso,
            mobile_money_provider=provider,
        ),
    )


def _merchant_request(
    merchant_key: str,
    store_id: str,
    balance_id: str,
    operator_id: int,
) -> CreatePaymentMethodRequest:
    return CreatePaymentMethodRequest(
        type=PaymentMethodType.NEXUS_MERCHANT,
        nexus_merchant_details=NexusMerchantDetails(
            merchant_key=merchant_key,
            store_id=store_id,
            balance_id=balance_id,
            operator_id=operator_id,
        ),
    )


# ---------------------------------------------------------------------------
# Sync
# ---------------------------------------------------------------------------

class PaymentMethodsResource(SyncResource):
    """Manage payment methods (Mobile Money, Merchant, Card, Person, PayPal)."""

    def create(self, request: CreatePaymentMethodRequest) -> PaymentMethod:
        """Create or retrieve an existing Payment Method.

        The API is idempotent on the underlying account details: calling
        ``create`` twice with the same phone number returns the same ID.
        """
        raw = self._post("/payment-methods", request.model_dump(by_alias=True, exclude_none=True))
        return PaymentMethod.model_validate(raw)

    def create_mobile_money(
        self,
        phone_number: str,
        country_iso: str,
        provider: MobileMoneyProvider,
    ) -> PaymentMethod:
        """Shortcut: create a Mobile Money payment method."""
        return self.create(_mobile_money_request(phone_number, country_iso, provider))

    def create_merchant(
        self,
        merchant_key: str,
        store_id: str,
        balance_id: str,
        operator_id: int,
    ) -> PaymentMethod:
        """Shortcut: create a Nexus Merchant payment method."""
        return self.create(_merchant_request(merchant_key, store_id, balance_id, operator_id))

    def list(self) -> list[PaymentMethod]:
        raw = self._get("/payment-methods")
        return PaymentMethodList.model_validate(raw).data

    def get(self, payment_method_id: str) -> PaymentMethod:
        raw = self._get(f"/payment-methods/{payment_method_id}")
        return PaymentMethod.model_validate(raw)

    def resolve_details(self, payment_method_id: str) -> dict[str, Any]:
        """Show the client information associated with a payment method."""
        return self._post(
            "/payment-methods/resolve-details",
            {"paymentMethodId": payment_method_id},
        )


# ---------------------------------------------------------------------------
# Async
# ---------------------------------------------------------------------------

class AsyncPaymentMethodsResource(AsyncResource):
    """Async variant of :class:`PaymentMethodsResource`."""

    async def create(self, request: CreatePaymentMethodRequest) -> PaymentMethod:
        raw = await self._post(
            "/payment-methods", request.model_dump(by_alias=True, exclude_none=True)
        )
        return PaymentMethod.model_validate(raw)

    async def create_mobile_money(
        self,
        phone_number: str,
        country_iso: str,
        provider: MobileMoneyProvider,
    ) -> PaymentMethod:
        return await self.create(_mobile_money_request(phone_number, country_iso, provider))

    async def create_merchant(
        self,
        merchant_key: str,
        store_id: str,
        balance_id: str,
        operator_id: int,
    ) -> PaymentMethod:
        return await self.create(_merchant_request(merchant_key, store_id, balance_id, operator_id))

    async def list(self) -> list[PaymentMethod]:
        raw = await self._get("/payment-methods")
        return PaymentMethodList.model_validate(raw).data

    async def get(self, payment_method_id: str) -> PaymentMethod:
        raw = await self._get(f"/payment-methods/{payment_method_id}")
        return PaymentMethod.model_validate(raw)

    async def resolve_details(self, payment_method_id: str) -> dict[str, Any]:
        return await self._post(
            "/payment-methods/resolve-details",
            {"paymentMethodId": payment_method_id},
        )
