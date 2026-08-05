"""Pydantic v2 request / response models — snake_case Python, camelCase API."""

from __future__ import annotations

from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field
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
    """Shared configuration for every model in this module.

    - ``alias_generator=to_camel`` maps Python ``snake_case`` fields to the
      API's ``camelCase`` keys, so we serialise with ``by_alias=True`` and
      validate incoming camelCase transparently.
    - ``populate_by_name=True`` still lets callers build models by Python name.
    - ``extra="allow"`` keeps unknown fields the API may add, so a server-side
      addition never breaks deserialisation.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",
    )


# ---------------------------------------------------------------------------
# Payment Methods
# ---------------------------------------------------------------------------

class MobileMoneyDetails(_Base):
    """Mobile Money account details (wallet phone number + operator).

    The API is asymmetric on the country field: requests expect ``countryIso``
    while responses echo it back as ``countryCode``. We therefore accept both
    on input and always serialise as ``countryIso``.
    """

    phone_number: str
    country_iso: str = Field(  # ISO 3166-1 alpha-2, e.g. "CM"
        validation_alias=AliasChoices("countryIso", "countryCode", "country_iso"),
        serialization_alias="countryIso",
    )
    mobile_money_provider: MobileMoneyProvider


class NexusMerchantDetails(_Base):
    """Identifiers of a Nexus merchant account used to collect/disburse."""

    merchant_key: str
    store_id: str
    balance_id: str
    operator_id: int


class NexusCardDetails(_Base):
    """Reference to a BaaS-issued card acting as a payment method."""

    card_id: int
    card_category: CardCategory


class PersonDetailsWithPhone(_Base):
    """Neero person identity addressed by phone number."""

    country_code: str
    phone_number: str


class PaypalDetails(_Base):
    """PayPal account details."""

    email: str
    country_iso: str


class CreatePaymentMethodRequest(_Base):
    """Body for ``POST /payment-methods``.

    Supply exactly one ``*_details`` block matching ``type``. Creation is
    idempotent on the underlying account, so re-creating the same wallet
    returns the same Payment Method id.
    """

    type: PaymentMethodType
    mobile_money_details: MobileMoneyDetails | None = None
    nexus_merchant_details: NexusMerchantDetails | None = None
    nexus_card_details: NexusCardDetails | None = None
    person_details_with_phone_number: PersonDetailsWithPhone | None = None
    paypal_details: PaypalDetails | None = None


class PaymentMethod(_Base):
    """A persistent payment method returned by the API (``id`` + details)."""

    id: str
    type: PaymentMethodType
    mobile_money_details: MobileMoneyDetails | None = None
    nexus_merchant_details: NexusMerchantDetails | None = None
    nexus_card_details: NexusCardDetails | None = None
    paypal_details: PaypalDetails | None = None


class PaymentMethodList(_Base):
    """Paginated envelope of :class:`PaymentMethod` objects."""

    data: list[PaymentMethod] = []


# ---------------------------------------------------------------------------
# Transaction Intents
# ---------------------------------------------------------------------------

class FlowTransaction(_Base):
    """One leg of a Nexus Flow split (marketplace fund distribution).

    Attached to a cash-in via ``flow_transactions`` to route part of the
    collected amount to another payment method automatically.
    """

    payment_method_id: str
    amount: int
    payment_type: PaymentType


class CreateTransactionIntentRequest(_Base):
    """Body for the cash-in / cash-out endpoints.

    Amounts are integers in the account currency (XAF, no decimals).
    ``platform_code`` is mandatory for COBAC/ANIF compliance and is injected
    by the resource layer from the client when the caller omits it.
    """

    source_payment_method_id: str
    destination_payment_method_id: str
    amount: int
    currency_code: str  # ISO 4217, e.g. "XAF"; required by the API
    payment_type: PaymentType
    platform_code: str
    external_transaction_id: str | None = None  # your own dedup reference
    flow_transactions: list[FlowTransaction] | None = None


class NextAction(_Base):
    """Action the payer must complete for the intent to progress.

    Present when the intent is in ``REQUIRES_ACTION`` (e.g. a redirect URL or
    a USSD push to confirm on the handset).
    """

    type: str
    redirect_url: str | None = None


class TransactionIntent(_Base):
    """The central transaction object returned by the API.

    ``status`` drives everything downstream — only
    :attr:`~nexus_africa.TransactionStatus.SUCCESSFUL` confirms settlement.
    """

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
    """Paginated envelope of :class:`TransactionIntent` objects."""

    data: list[TransactionIntent] = []
    total: int | None = None
    page: int | None = None
    page_size: int | None = None


# ---------------------------------------------------------------------------
# Balances
# ---------------------------------------------------------------------------

class Balance(_Base):
    """Balance of a merchant payment method.

    Note: field shape (``amount`` / ``currency`` / ``available``) is inferred
    and pending confirmation against the live sandbox.
    """

    payment_method_id: str | None = None
    amount: int | None = None
    currency: str | None = None
    available: int | None = None  # spendable portion, excluding holds


# ---------------------------------------------------------------------------
# Sessions (hosted payment)
# ---------------------------------------------------------------------------

class DisplayInfo(_Base):
    """Branding shown on the hosted checkout page."""

    title: str | None = None
    description: str | None = None
    logo_url: str | None = None


class CreateSessionRequest(_Base):
    """Body for ``POST /sessions`` — wraps an existing Transaction Intent."""

    transaction_intent_id: str
    return_url: str | None = None
    display_info: DisplayInfo | None = None


class Session(_Base):
    """A hosted payment session; redirect the payer to ``payment_link``."""

    id: str
    payment_link: str | None = None
    transaction_intent_id: str | None = None
    status: str | None = None
    expires_at: str | None = None


# ---------------------------------------------------------------------------
# Webhooks
# ---------------------------------------------------------------------------

class OperatorDetails(_Base):
    """Merchant/operator context attached to a webhook event."""

    operator_id: int | None = None
    merchant_key: str | None = None


class WebhookEventData(_Base):
    """Event payload wrapper — ``object`` holds the changed resource."""

    object: dict[str, Any] = {}


class WebhookEvent(_Base):
    """A verified webhook event.

    ``type`` stays permissive (enum *or* raw string) so an event type added
    server-side never fails validation. The convenience properties reach into
    the untyped ``data.object`` for the two fields most callers need.
    """

    id: str
    type: WebhookEventType | str
    data: WebhookEventData
    operator_details: OperatorDetails | None = None

    @property
    def transaction_intent_id(self) -> str | None:
        """Id of the affected Transaction Intent, if this is a TI event."""
        return self.data.object.get("transactionIntentId")

    @property
    def new_status(self) -> str | None:
        """New status carried by a ``*.statusUpdated`` event, if any."""
        return self.data.object.get("newStatus")


# ---------------------------------------------------------------------------
# BaaS — Config
# ---------------------------------------------------------------------------

class Nationality(_Base):
    """A nationality option accepted during KYC onboarding."""

    code: str
    name: str | None = None


class RequiredDocument(_Base):
    """A KYC document the onboarding flow expects for a given nationality."""

    type: str
    label: str | None = None
    required: bool | None = None


# ---------------------------------------------------------------------------
# BaaS — Onboarding
# ---------------------------------------------------------------------------

class CreateOnboardingSessionRequest(_Base):
    """Body to open a KYC onboarding session."""

    nationality_code: str | None = None
    document_type: str | None = None


class OnboardingSession(_Base):
    """A KYC onboarding session; ``status`` tracks review progress."""

    id: str
    status: OnboardingSessionStatus | None = None
    created_at: str | None = None


# ---------------------------------------------------------------------------
# BaaS — Party
# ---------------------------------------------------------------------------

class Party(_Base):
    """A KYC-validated identity that can hold cards."""

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
    """Body to issue a card for a Party (virtual only for now)."""

    party_id: str
    card_category: CardCategory = CardCategory.VIRTUAL


class Card(_Base):
    """An issued card. PCI-sensitive fields are never included here."""

    id: int
    category: CardCategory | None = None
    status: str | None = None
    last_four: str | None = None  # safe display digits
    expiry_month: int | None = None
    expiry_year: int | None = None
    created_at: str | None = None


class CardViewLink(_Base):
    """Short-lived URL to display masked card details in an iframe."""

    url: str | None = None
    expires_at: str | None = None


class CardSecureDetails(_Base):
    """Full PCI card data (PAN, CVV, expiry). Handle with care; never log."""

    card_number: str | None = None
    cvv: str | None = None
    expiry_month: int | None = None
    expiry_year: int | None = None
