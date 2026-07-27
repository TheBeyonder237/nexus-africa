"""Enumerations mirroring the closed value sets of the Nexus / Neero API.

Every enum subclasses :class:`~enum.StrEnum`, so members compare equal to and
serialise as their raw string value — they can be passed anywhere the API
expects the underlying code, and Pydantic round-trips them transparently.
"""

from __future__ import annotations

import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:  # pragma: no cover - Python 3.10 fallback (StrEnum is 3.11+)
    from enum import Enum

    class StrEnum(str, Enum):
        """Minimal StrEnum backport for Python 3.10."""

        def __str__(self) -> str:
            return str(self.value)


class Environment(StrEnum):
    """Target API environment.

    ``SANDBOX`` points at the Neero test gateway (fake providers, test
    numbers); ``LIVE`` at production. The client selects the environment
    through its ``sandbox`` flag rather than this enum directly.
    """

    SANDBOX = "sandbox"
    LIVE = "live"


class PaymentMethodType(StrEnum):
    """Kind of account a :class:`~nexus_africa.PaymentMethod` represents.

    A Payment Method is the persistent, idempotent handle Nexus uses on both
    ends of a transaction (source and destination).
    """

    MOBILE_MONEY = "MOBILE_MONEY"  # end-user MTN / Orange wallet
    NEXUS_MERCHANT = "NEXUS_MERCHANT"  # your collecting merchant account
    NEXUS_CARD = "NEXUS_CARD"  # BaaS-issued virtual card
    NEERO_PERSON = "NEERO_PERSON"  # a KYC-onboarded Neero identity
    PAYPAL = "PAYPAL"


class MobileMoneyProvider(StrEnum):
    """Mobile Money operator backing a wallet in the CEMAC zone."""

    ORANGE_MONEY = "ORANGE_MONEY"  # Cameroon prefixes 69x / 65x-Orange
    MTN_MONEY = "MTN_MONEY"  # Cameroon prefixes 67x / 65x-MTN


class TransactionType(StrEnum):
    """Direction of funds, derived by the API from source/destination.

    Reported on a :class:`~nexus_africa.TransactionIntent`; you never set it
    yourself — the cash-in / cash-out endpoint determines it.
    """

    CASHIN = "CASHIN"  # Mobile Money -> Merchant (collection)
    CASHOUT = "CASHOUT"  # Merchant -> Mobile Money (payout)
    EXTERNAL = "EXTERNAL"  # off-platform movement


class PaymentType(StrEnum):
    """Payment rail selected for a transaction or Nexus Flow leg."""

    MERCHANT_COLLECTION = "MERCHANT_COLLECTION"  # default for cash-in
    ORANGE_MONEY_TRANSFER = "ORANGE_MONEY_TRANSFER"
    MTN_MONEY_TRANSFER = "MTN_MONEY_TRANSFER"
    TRANSFER_TO_NEERO_PERSON = "TRANSFER_TO_NEERO_PERSON"
    TRANSFER_TO_NEERO_MERCHANT = "TRANSFER_TO_NEERO_MERCHANT"


class TransactionStatus(StrEnum):
    """Lifecycle state of a Transaction Intent.

    Nominal progression::

        INITIALIZED -> REQUIRES_PAYMENT_METHOD -> WAITING_FOR_CONFIRMATION
        -> REQUIRES_ACTION -> PENDING -> SUCCESSFUL

    with ``FAILED``, ``CANCELLED``, ``EXPIRED`` and ``REFUNDED`` as terminal
    off-ramps. Only ``SUCCESSFUL`` guarantees the funds moved.
    """

    INITIALIZED = "INITIALIZED"
    REQUIRES_PAYMENT_METHOD = "REQUIRES_PAYMENT_METHOD"
    WAITING_FOR_CONFIRMATION = "WAITING_FOR_CONFIRMATION"
    REQUIRES_ACTION = "REQUIRES_ACTION"  # e.g. USSD push awaiting the payer
    PENDING = "PENDING"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"
    SUCCESSFUL = "SUCCESSFUL"
    REFUNDED = "REFUNDED"


class WebhookEventType(StrEnum):
    """``type`` field carried by an incoming webhook event."""

    TRANSACTION_INTENT_STATUS_UPDATED = "transactionIntent.statusUpdated"
    PARTY_ONBOARDING_SESSION_STATUS_UPDATED = "partyOnboardingSession.statusUpdated"
    CARD_MANAGEMENT_ONLINE_TRANSACTIONS = "cardManagement.onlineTransactions"


class CardCategory(StrEnum):
    """Category of a BaaS-issued card. Only virtual cards exist today."""

    VIRTUAL = "VIRTUAL"


class OnboardingSessionStatus(StrEnum):
    """State of a BaaS KYC onboarding session.

    ``PENDING`` (documents expected) -> ``SUBMITTED`` (under review) ->
    ``APPROVED`` (Party created) or ``REJECTED``.
    """

    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
