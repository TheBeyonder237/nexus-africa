"""Transaction Intents resource — cash-in, cash-out, confirm, cancel, list."""

from __future__ import annotations

from .._enums import PaymentType
from .._models import (
    CreateTransactionIntentRequest,
    FlowTransaction,
    TransactionIntent,
    TransactionIntentList,
)
from ._base import AsyncResource, SyncResource


def _build_request(
    source_payment_method_id: str,
    destination_payment_method_id: str,
    amount: int,
    payment_type: PaymentType,
    platform_code: str,
    external_transaction_id: str | None,
    flow_transactions: list[FlowTransaction] | None,
) -> CreateTransactionIntentRequest:
    return CreateTransactionIntentRequest(
        source_payment_method_id=source_payment_method_id,
        destination_payment_method_id=destination_payment_method_id,
        amount=amount,
        payment_type=payment_type,
        platform_code=platform_code,
        external_transaction_id=external_transaction_id,
        flow_transactions=flow_transactions,
    )


# ---------------------------------------------------------------------------
# Sync
# ---------------------------------------------------------------------------

class TransactionIntentsResource(SyncResource):
    """Create and manage Transaction Intents (cash-in / cash-out)."""

    def cash_in(
        self,
        *,
        source_payment_method_id: str,
        destination_payment_method_id: str,
        amount: int,
        payment_type: PaymentType = PaymentType.MERCHANT_COLLECTION,
        platform_code: str | None = None,
        external_transaction_id: str | None = None,
        flow_transactions: list[FlowTransaction] | None = None,
        idempotency_key: str | None = None,
    ) -> TransactionIntent:
        """Initiate a cash-in (client → merchant).

        Args:
            source_payment_method_id:      Client's Mobile Money PM id.
            destination_payment_method_id: Merchant PM id.
            amount:                        Amount in XAF (integer).
            payment_type:                  Defaults to MERCHANT_COLLECTION.
            platform_code:                 Mandatory for COBAC/ANIF compliance.
                                           Falls back to ``client.platform_code``.
            external_transaction_id:       Your own reference (dedup key).
            flow_transactions:             Nexus Flow distribution rules.
            idempotency_key:               ``X-IDEMPOTENCY-KEY`` header value.
        """
        req = _build_request(
            source_payment_method_id,
            destination_payment_method_id,
            amount,
            payment_type,
            platform_code or self._client.platform_code,
            external_transaction_id,
            flow_transactions,
        )
        raw = self._post(
            "/transaction-intents/cash-in",
            req.model_dump(by_alias=True, exclude_none=True),
            idempotency_key=idempotency_key,
        )
        return TransactionIntent.model_validate(raw)

    def cash_out(
        self,
        *,
        source_payment_method_id: str,
        destination_payment_method_id: str,
        amount: int,
        payment_type: PaymentType = PaymentType.ORANGE_MONEY_TRANSFER,
        platform_code: str | None = None,
        external_transaction_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> TransactionIntent:
        """Initiate a cash-out (merchant → recipient's Mobile Money).

        Args:
            source_payment_method_id:      Merchant PM id.
            destination_payment_method_id: Recipient's Mobile Money PM id.
            amount:                        Amount in XAF (integer).
            payment_type:                  e.g. ORANGE_MONEY_TRANSFER or MTN_MONEY_TRANSFER.
            platform_code:                 Falls back to ``client.platform_code``.
            external_transaction_id:       Your own reference.
            idempotency_key:               ``X-IDEMPOTENCY-KEY`` header value.
        """
        req = _build_request(
            source_payment_method_id,
            destination_payment_method_id,
            amount,
            payment_type,
            platform_code or self._client.platform_code,
            external_transaction_id,
            None,
        )
        raw = self._post(
            "/transaction-intents/cash-out",
            req.model_dump(by_alias=True, exclude_none=True),
            idempotency_key=idempotency_key,
        )
        return TransactionIntent.model_validate(raw)

    def get(self, intent_id: str) -> TransactionIntent:
        """Retrieve a single Transaction Intent by ID."""
        raw = self._get(f"/transaction-intents/{intent_id}")
        return TransactionIntent.model_validate(raw)

    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        status: str | None = None,
    ) -> TransactionIntentList:
        """List Transaction Intents with optional filtering."""
        params = {k: v for k, v in {"page": page, "pageSize": page_size, "status": status}.items() if v is not None}
        raw = self._get("/transaction-intents", **params)
        return TransactionIntentList.model_validate(raw)

    def confirm(self, intent_id: str) -> TransactionIntent:
        """Manually confirm a transaction in WAITING_FOR_CONFIRMATION status."""
        raw = self._post(f"/transaction-intents/{intent_id}/confirm")
        return TransactionIntent.model_validate(raw)

    def cancel(self, intent_id: str) -> TransactionIntent:
        """Cancel a transaction that has not yet been executed."""
        raw = self._patch(f"/transaction-intents/{intent_id}/cancel")
        return TransactionIntent.model_validate(raw)


# ---------------------------------------------------------------------------
# Async
# ---------------------------------------------------------------------------

class AsyncTransactionIntentsResource(AsyncResource):
    """Async variant of :class:`TransactionIntentsResource`."""

    async def cash_in(
        self,
        *,
        source_payment_method_id: str,
        destination_payment_method_id: str,
        amount: int,
        payment_type: PaymentType = PaymentType.MERCHANT_COLLECTION,
        platform_code: str | None = None,
        external_transaction_id: str | None = None,
        flow_transactions: list[FlowTransaction] | None = None,
        idempotency_key: str | None = None,
    ) -> TransactionIntent:
        req = _build_request(
            source_payment_method_id,
            destination_payment_method_id,
            amount,
            payment_type,
            platform_code or self._client.platform_code,
            external_transaction_id,
            flow_transactions,
        )
        raw = await self._post(
            "/transaction-intents/cash-in",
            req.model_dump(by_alias=True, exclude_none=True),
            idempotency_key=idempotency_key,
        )
        return TransactionIntent.model_validate(raw)

    async def cash_out(
        self,
        *,
        source_payment_method_id: str,
        destination_payment_method_id: str,
        amount: int,
        payment_type: PaymentType = PaymentType.ORANGE_MONEY_TRANSFER,
        platform_code: str | None = None,
        external_transaction_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> TransactionIntent:
        req = _build_request(
            source_payment_method_id,
            destination_payment_method_id,
            amount,
            payment_type,
            platform_code or self._client.platform_code,
            external_transaction_id,
            None,
        )
        raw = await self._post(
            "/transaction-intents/cash-out",
            req.model_dump(by_alias=True, exclude_none=True),
            idempotency_key=idempotency_key,
        )
        return TransactionIntent.model_validate(raw)

    async def get(self, intent_id: str) -> TransactionIntent:
        raw = await self._get(f"/transaction-intents/{intent_id}")
        return TransactionIntent.model_validate(raw)

    async def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        status: str | None = None,
    ) -> TransactionIntentList:
        params = {k: v for k, v in {"page": page, "pageSize": page_size, "status": status}.items() if v is not None}
        raw = await self._get("/transaction-intents", **params)
        return TransactionIntentList.model_validate(raw)

    async def confirm(self, intent_id: str) -> TransactionIntent:
        raw = await self._post(f"/transaction-intents/{intent_id}/confirm")
        return TransactionIntent.model_validate(raw)

    async def cancel(self, intent_id: str) -> TransactionIntent:
        raw = await self._patch(f"/transaction-intents/{intent_id}/cancel")
        return TransactionIntent.model_validate(raw)
