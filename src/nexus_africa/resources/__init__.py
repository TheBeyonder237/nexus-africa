"""Resource classes exposed as attributes on the clients.

Each pair (sync + async) maps a Nexus domain to its endpoints:
``payment_methods``, ``intents``, ``balances``, ``sessions`` on the gateway,
and ``baas`` (config / onboarding / parties / cards) on the BaaS base URL.
"""

from .baas import AsyncBaaSResource, BaaSResource
from .balances import AsyncBalancesResource, BalancesResource
from .payment_methods import AsyncPaymentMethodsResource, PaymentMethodsResource
from .sessions import AsyncSessionsResource, SessionsResource
from .transaction_intents import AsyncTransactionIntentsResource, TransactionIntentsResource

__all__ = [
    "PaymentMethodsResource",
    "AsyncPaymentMethodsResource",
    "TransactionIntentsResource",
    "AsyncTransactionIntentsResource",
    "BalancesResource",
    "AsyncBalancesResource",
    "SessionsResource",
    "AsyncSessionsResource",
    "BaaSResource",
    "AsyncBaaSResource",
]
