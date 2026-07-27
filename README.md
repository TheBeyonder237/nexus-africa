# nexus-africa

Async-first Python SDK for the [Nexus/Neero](https://docs.nexus-africa.io) payment gateway (CEMAC zone — Cameroon, Central Africa).

## Why this SDK?

The official `neero-gateway` uses stdlib only (synchronous). This SDK adds:

- **Async-first** via `httpx` — drop-in for FastAPI / async frameworks
- **Pydantic v2 models** — typed request and response objects
- **Typed exceptions** — one class per error family (`PaymentMethodError`, `GatewayError`, `IdempotencyConflict`…)
- **Full endpoint coverage** — Payment Methods, Transaction Intents, Balances, Sessions, BaaS (cards, KYC onboarding)
- **Webhook helper** — `verify_and_parse()` with HMAC-SHA512 + replay protection

## Installation

```bash
pip install nexus-africa
```

## Quick start — sync

```python
from nexus_africa import NexusClient, MobileMoneyProvider, PaymentType

with NexusClient("sk_test_...", platform_code="MYAPP") as client:
    # 1. Register the client's Mobile Money wallet
    client_pm = client.payment_methods.create_mobile_money(
        "+237691111111", "CM", MobileMoneyProvider.ORANGE_MONEY
    )
    # 2. Register your Nexus Merchant account
    merchant_pm = client.payment_methods.create_merchant(
        merchant_key="mk_...",
        store_id="store_...",
        balance_id="bal_...",
        operator_id=9,
    )
    # 3. Initiate cash-in (client → merchant)
    intent = client.intents.cash_in(
        source_payment_method_id=client_pm.id,
        destination_payment_method_id=merchant_pm.id,
        amount=5000,                    # XAF, integer
        idempotency_key="order_42",     # optional but recommended
    )
    print(intent.status)  # PENDING
    print(intent.id)      # intent_...
```

## Quick start — async

```python
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
```

## Webhook verification

```python
from nexus_africa.webhook import verify_and_parse

# In your FastAPI route:
async def nexus_webhook(request: Request):
    raw_body = await request.body()
    event = verify_and_parse(
        raw_body=raw_body,
        timestamp=request.headers["X-TIMESTAMP"],
        signature=request.headers["X-SIGNATURE"],
        secret="wh_secret_from_dashboard",
        max_age_seconds=300,       # replay protection
    )
    if event.new_status == "SUCCESSFUL":
        await handle_payment_success(event.transaction_intent_id)
    return {"received": True}
```

## Cash-out (payout)

```python
intent = client.intents.cash_out(
    source_payment_method_id=merchant_pm.id,
    destination_payment_method_id=recipient_pm.id,
    amount=10000,
    payment_type=PaymentType.MTN_MONEY_TRANSFER,
    external_transaction_id="payout_driver_42",
)
```

## Nexus Flow (marketplace split)

```python
from nexus_africa import FlowTransaction, PaymentType

intent = client.intents.cash_in(
    source_payment_method_id=client_pm.id,
    destination_payment_method_id=merchant_pm.id,
    amount=10000,
    flow_transactions=[
        FlowTransaction(
            payment_method_id=partner_pm.id,
            amount=1500,
            payment_type=PaymentType.TRANSFER_TO_NEERO_PERSON,
        )
    ],
)
```

## Hosted payment session

```python
session = client.sessions.create(
    transaction_intent_id=intent.id,
    return_url="https://myapp.com/payment/callback",
    title="Ma commande #42",
)
# Redirect the user to:
print(session.payment_link)
```

## Error handling

```python
from nexus_africa import (
    IdempotencyConflict,
    GatewayError,
    PaymentMethodError,
    TransactionIntentError,
)

try:
    intent = client.intents.cash_in(...)
except IdempotencyConflict:
    # GE-0002 — transaction already exists, treat as success
    intent = client.intents.get(existing_id)
except GatewayError as e:
    # gtw-4004 insufficient funds, gtw-4012 rejected by client, etc.
    print(e.code, e.message)
except TransactionIntentError as e:
    # TI-0014 missing platform code, TI-0016 duplicate external ID, etc.
    print(e.code, e.message)
```

## Test numbers (sandbox)

| Prefix | Provider      | Suffix      | Result     |
|--------|---------------|-------------|------------|
| `65x`  | MTN MoMo      | `...1111111` | SUCCESSFUL |
| `65x`  | MTN MoMo      | `...2222222` | FAILED     |
| `65x`  | MTN MoMo      | `...3333333` | PENDING    |
| `69x`  | Orange Money  | `...1111111` | SUCCESSFUL |
| `69x`  | Orange Money  | `...2222222` | FAILED     |

Example: `+237651111111` → MTN, SUCCESSFUL.

## BaaS (card issuance)

```python
# KYC onboarding
session = client.baas.onboarding.create_session(nationality_code="CM")
session = client.baas.onboarding.submit_session(session.id)
party = client.baas.onboarding.get_party(session.id)

# Issue a virtual card
card = client.baas.cards.create_virtual(party_id=party.id)
link = client.baas.cards.get_view_link(card.id)
```

## Environments

```python
# Sandbox (default)
client = NexusClient("test_sk_...", platform_code="X", sandbox=True)

# Live / production
client = NexusClient("live_sk_...", platform_code="X", sandbox=False)
```

## License

MIT
