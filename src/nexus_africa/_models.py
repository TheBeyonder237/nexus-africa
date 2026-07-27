"""Pydantic v2 request / response models — snake_case Python, camelCase API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from ._enums import (
    CardCategory,
    MobileMoneyProvider,
    OnboardingSessionStatus,
    PaymentMethodType,
    PaymentType,
    TransactionStatus,
    TransactionType,
    WebhookEventType,
)


class _Base(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",
    )


# ---------------------------------------------------------------------------
# Payment Methods
# ---------------------------------------------------------------------------

class MobileMoneyDetails(_Base):
    phone_number: str
    country_iso: str
    mobile_money_provider: MobileMoneyProvider


class NexusMerchantDetails(_Base):
    merchant_key: str
    store_id: str
    balance_id: str
    operator_id: int


class NexusCardDetails(_Base):
    card_id: int
    card_category: CardCategory


class PersonDetailsWithPhone(_Base):
    country_code: str
    phone_number: str


class PaypalDetails(_Base):
    email: str
    country_iso: str


class CreatePaymentMethodRequest(_Base):
    type: PaymentMethodType
    mobile_money_details: MobileMoneyDetails | None = None
    nexus_merchant_details: NexusMerchantDetails | None = None
    nexus_card_details: NexusCardDetails | None = None
    person_details_with_phone_number: PersonDetailsWithPhone | None = None
    paypal_details: PaypalDetails | None = None


class PaymentMethod(_Base):
    id: str
    type: PaymentMethodType
    mobile_money_details: MobileMoneyDetails | None = None
    nexus_merchant_details: NexusMerchantDetails | None = None
    nexus_card_details: NexusCardDetails | None = None
    paypal_details: PaypalDetails | None = None


class PaymentMethodList(_Base):
    data: list[PaymentMethod] = []


# ---------------------------------------------------------------------------
# Transaction Intents
# ---------------------------------------------------------------------------

class FlowTransaction(_Base):
    payment_method_id: str
    amount: int
    payment_type: PaymentType


class CreateTransactionIntentRequest(_Base):
    source_payment_method_id: str
    destination_payment_method_id: str
    amount: int
    payment_type: PaymentType
    platform_code: str
    external_transaction_id: str | None = None
    flow_transactions: list[FlowTransaction] | None = None


class NextAction(_Base):
    type: str
    redirect_url: str | None = None


class TransactionIntent(_Base):
    id: str
    status: TransactionStatus
    transaction_type: TransactionType | None = None
    amount: int
    payment_type: PaymentType | None = None
    source_payment_method_id: str | None = None
    destination_payment_method_id: str | None = None
    platform_code: str | None = None
    external_transaction_id: str | None = None
    next_action: NextAction | None = None
    flow_transactions: list[Any] | None = None
    created_at: str | None = None
    updated_at: str | None = None


class TransactionIntentList(_Base):
    data: list[TransactionIntent] = []
    total: int | None = None
    page: int | None = None
    page_size: int | None = None


# ---------------------------------------------------------------------------
# Balances
# ---------------------------------------------------------------------------

class Balance(_Base):
    payment_method_id: str | None = None
    amount: int | None = None
    currency: str | None = None
    available: int | None = None


# ---------------------------------------------------------------------------
# Sessions (hosted payment)
# ---------------------------------------------------------------------------

class DisplayInfo(_Base):
    title: str | None = None
    description: str | None = None
    logo_url: str | None = None


class CreateSessionRequest(_Base):
    transaction_intent_id: str
    return_url: str | None = None
    display_info: DisplayInfo | None = None


class Session(_Base):
    id: str
    payment_link: str | None = None
    transaction_intent_id: str | None = None
    status: str | None = None
    expires_at: str | None = None


# ---------------------------------------------------------------------------
# Webhooks
# ---------------------------------------------------------------------------

class OperatorDetails(_Base):
    operator_id: int | None = None
    merchant_key: str | None = None


class WebhookEventData(_Base):
    object: dict[str, Any] = {}


class WebhookEvent(_Base):
    id: str
    type: WebhookEventType | str
    data: WebhookEventData
    operator_details: OperatorDetails | None = None

    @property
    def transaction_intent_id(self) -> str | None:
        return self.data.object.get("transactionIntentId")

    @property
    def new_status(self) -> str | None:
        return self.data.object.get("newStatus")


# ---------------------------------------------------------------------------
# BaaS — Config
# ---------------------------------------------------------------------------

class Nationality(_Base):
    code: str
    name: str | None = None


class RequiredDocument(_Base):
    type: str
    label: str | None = None
    required: bool | None = None


# ---------------------------------------------------------------------------
# BaaS — Onboarding
# ---------------------------------------------------------------------------

class CreateOnboardingSessionRequest(_Base):
    nationality_code: str | None = None
    document_type: str | None = None


class OnboardingSession(_Base):
    id: str
    status: OnboardingSessionStatus | None = None
    created_at: str | None = None


# ---------------------------------------------------------------------------
# BaaS — Party
# ---------------------------------------------------------------------------

class Party(_Base):
    id: str
    status: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    created_at: str | None = None


# ---------------------------------------------------------------------------
# BaaS — Cards
# ---------------------------------------------------------------------------

class CreateCardRequest(_Base):
    party_id: str
    card_category: CardCategory = CardCategory.VIRTUAL


class Card(_Base):
    id: int
    category: CardCategory | None = None
    status: str | None = None
    last_four: str | None = None
    expiry_month: int | None = None
    expiry_year: int | None = None
    created_at: str | None = None


class CardViewLink(_Base):
    url: str | None = None
    expires_at: str | None = None


class CardSecureDetails(_Base):
    card_number: str | None = None
    cvv: str | None = None
    expiry_month: int | None = None
    expiry_year: int | None = None
