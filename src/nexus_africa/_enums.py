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
    SANDBOX = "sandbox"
    LIVE = "live"


class PaymentMethodType(StrEnum):
    MOBILE_MONEY = "MOBILE_MONEY"
    NEXUS_MERCHANT = "NEXUS_MERCHANT"
    NEXUS_CARD = "NEXUS_CARD"
    NEERO_PERSON = "NEERO_PERSON"
    PAYPAL = "PAYPAL"


class MobileMoneyProvider(StrEnum):
    ORANGE_MONEY = "ORANGE_MONEY"
    MTN_MONEY = "MTN_MONEY"


class TransactionType(StrEnum):
    CASHIN = "CASHIN"
    CASHOUT = "CASHOUT"
    EXTERNAL = "EXTERNAL"


class PaymentType(StrEnum):
    MERCHANT_COLLECTION = "MERCHANT_COLLECTION"
    ORANGE_MONEY_TRANSFER = "ORANGE_MONEY_TRANSFER"
    MTN_MONEY_TRANSFER = "MTN_MONEY_TRANSFER"
    TRANSFER_TO_NEERO_PERSON = "TRANSFER_TO_NEERO_PERSON"
    TRANSFER_TO_NEERO_MERCHANT = "TRANSFER_TO_NEERO_MERCHANT"


class TransactionStatus(StrEnum):
    INITIALIZED = "INITIALIZED"
    REQUIRES_PAYMENT_METHOD = "REQUIRES_PAYMENT_METHOD"
    WAITING_FOR_CONFIRMATION = "WAITING_FOR_CONFIRMATION"
    REQUIRES_ACTION = "REQUIRES_ACTION"
    PENDING = "PENDING"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"
    SUCCESSFUL = "SUCCESSFUL"
    REFUNDED = "REFUNDED"


class WebhookEventType(StrEnum):
    TRANSACTION_INTENT_STATUS_UPDATED = "transactionIntent.statusUpdated"
    PARTY_ONBOARDING_SESSION_STATUS_UPDATED = "partyOnboardingSession.statusUpdated"
    CARD_MANAGEMENT_ONLINE_TRANSACTIONS = "cardManagement.onlineTransactions"


class CardCategory(StrEnum):
    VIRTUAL = "VIRTUAL"


class OnboardingSessionStatus(StrEnum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
