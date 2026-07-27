"""nexus-africa — async-first Python SDK for the Nexus/Neero payment gateway.

Quick start (sync)::

    from nexus_africa import NexusClient, MobileMoneyProvider

    with NexusClient("sk_test_...", platform_code="MYAPP") as client:
        pm = client.payment_methods.create_mobile_money(
            "+237691111111", "CM", MobileMoneyProvider.ORANGE_MONEY
        )
        intent = client.intents.cash_in(
            source_payment_method_id=pm.id,
            destination_payment_method_id="<merchant_pm_id>",
            amount=5000,
        )
        print(intent.status)  # PENDING

Quick start (async)::

    import asyncio
    from nexus_africa import AsyncNexusClient, MobileMoneyProvider

    async def main():
        async with AsyncNexusClient("sk_test_...", platform_code="MYAPP") as client:
            pm = await client.payment_methods.create_mobile_money(
                "+237651111111", "CM", MobileMoneyProvider.MTN_MONEY
            )
            intent = await client.intents.cash_in(
                source_payment_method_id=pm.id,
                destination_payment_method_id="<merchant_pm_id>",
                amount=5000,
            )
            print(intent.status)

    asyncio.run(main())

Webhook verification::

    from nexus_africa.webhook import verify_and_parse

    event = verify_and_parse(raw_body, timestamp, signature, secret)
    if event.new_status == "SUCCESSFUL":
        ...
"""

from ._client import AsyncNexusClient, NexusClient
from ._enums import (
    CardCategory,
    Environment,
    MobileMoneyProvider,
    OnboardingSessionStatus,
    PaymentMethodType,
    PaymentType,
    TransactionStatus,
    TransactionType,
    WebhookEventType,
)
from ._exceptions import (
    AuthError,
    BalanceError,
    GatewayError,
    GeneralError,
    IdempotencyConflict,
    NexusError,
    PaymentMethodError,
    RateLimitError,
    ServerError,
    SessionError,
    TransactionIntentError,
    VerificationError,
)
from ._models import (
    Balance,
    Card,
    CardSecureDetails,
    CardViewLink,
    CreatePaymentMethodRequest,
    CreateSessionRequest,
    CreateTransactionIntentRequest,
    DisplayInfo,
    FlowTransaction,
    MobileMoneyDetails,
    NexusMerchantDetails,
    Party,
    PaymentMethod,
    Session,
    TransactionIntent,
    TransactionIntentList,
    WebhookEvent,
)
from . import _webhook as webhook

__version__ = "0.1.0"

__all__ = [
    # Clients
    "NexusClient",
    "AsyncNexusClient",
    # Enums
    "Environment",
    "PaymentMethodType",
    "MobileMoneyProvider",
    "TransactionType",
    "PaymentType",
    "TransactionStatus",
    "WebhookEventType",
    "CardCategory",
    "OnboardingSessionStatus",
    # Models
    "MobileMoneyDetails",
    "NexusMerchantDetails",
    "CreatePaymentMethodRequest",
    "PaymentMethod",
    "FlowTransaction",
    "CreateTransactionIntentRequest",
    "TransactionIntent",
    "TransactionIntentList",
    "Balance",
    "DisplayInfo",
    "CreateSessionRequest",
    "Session",
    "WebhookEvent",
    "Party",
    "Card",
    "CardViewLink",
    "CardSecureDetails",
    # Exceptions
    "NexusError",
    "AuthError",
    "PaymentMethodError",
    "TransactionIntentError",
    "VerificationError",
    "GatewayError",
    "GeneralError",
    "BalanceError",
    "SessionError",
    "IdempotencyConflict",
    "RateLimitError",
    "ServerError",
    # Webhook module
    "webhook",
    # Version
    "__version__",
]
