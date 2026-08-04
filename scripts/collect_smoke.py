"""Live 'collect' (cash-in) diagnostic against the Nexus sandbox.

Runs the full collection flow — create merchant, create payer Mobile Money,
then cash-in — and prints the exact error shape (code / message / detail /
http_status / error_data) at whichever step fails. Useful to see *why* a
collect is rejected by the real API.

Credentials are read from environment variables so nothing sensitive is
committed. Run it from a machine whose public IP is allow-listed in the Nexus
dashboard, otherwise every call returns ``403 GE-0004 "Ip not allowed"`` before
reaching the collect logic.

Usage (PowerShell)::

    $env:NEXUS_SECRET       = "sk_test_..."
    $env:NEXUS_PLATFORM     = "PLF-...."
    $env:NEXUS_MERCHANT_KEY = "mk_..."
    $env:NEXUS_STORE_ID     = "...."
    $env:NEXUS_BALANCE_ID   = "...."
    $env:NEXUS_OPERATOR_ID  = "210"
    python scripts/collect_smoke.py

Usage (bash)::

    NEXUS_SECRET=sk_test_... NEXUS_PLATFORM=PLF-... ... python scripts/collect_smoke.py

Optional overrides: ``NEXUS_PAYER`` (default ``+237651111111``, an MTN sandbox
number that resolves to SUCCESSFUL) and ``NEXUS_AMOUNT`` (default ``100``).
"""

from __future__ import annotations

import os
import sys
import traceback

from nexus_africa import MobileMoneyProvider, NexusClient
from nexus_africa._exceptions import NexusError

REQUIRED = [
    "NEXUS_SECRET",
    "NEXUS_PLATFORM",
    "NEXUS_MERCHANT_KEY",
    "NEXUS_STORE_ID",
    "NEXUS_BALANCE_ID",
    "NEXUS_OPERATOR_ID",
]


def _env() -> dict[str, str]:
    missing = [name for name in REQUIRED if not os.environ.get(name)]
    if missing:
        print("Missing environment variables: " + ", ".join(missing))
        sys.exit(2)
    return {name: os.environ[name] for name in REQUIRED}


def _dump_error(step: str, exc: Exception) -> None:
    print(f"  [{step}] FAILED")
    if isinstance(exc, NexusError):
        print(f"    code       : {exc.code}")
        print(f"    message    : {exc.message}")
        print(f"    detail     : {exc.detail}")
        print(f"    http_status: {exc.http_status}")
        print(f"    error_data : {exc.error_data}")
    else:
        print(f"    {type(exc).__name__}: {exc}")


def main() -> None:
    env = _env()
    payer_phone = os.environ.get("NEXUS_PAYER", "+237651111111")
    amount = int(os.environ.get("NEXUS_AMOUNT", "100"))

    print(f"platform={env['NEXUS_PLATFORM']}  payer={payer_phone}  amount={amount}")

    with NexusClient(
        env["NEXUS_SECRET"], platform_code=env["NEXUS_PLATFORM"], sandbox=True
    ) as client:
        # 1. Merchant — the collection destination.
        try:
            merchant = client.payment_methods.create_merchant(
                env["NEXUS_MERCHANT_KEY"],
                env["NEXUS_STORE_ID"],
                env["NEXUS_BALANCE_ID"],
                int(env["NEXUS_OPERATOR_ID"]),
            )
            print(f"  [merchant] ok id={merchant.id}")
        except Exception as exc:  # noqa: BLE001 - diagnostic tool, report anything
            _dump_error("merchant", exc)
            return

        # 2. Payer Mobile Money — the collection source.
        try:
            payer = client.payment_methods.create_mobile_money(
                payer_phone, "CM", MobileMoneyProvider.MTN_MONEY
            )
            print(f"  [payer] ok id={payer.id}")
        except Exception as exc:  # noqa: BLE001
            _dump_error("payer", exc)
            return

        # 3. The collect itself.
        try:
            intent = client.intents.cash_in(
                source_payment_method_id=payer.id,
                destination_payment_method_id=merchant.id,
                amount=amount,
            )
            print("  [collect] ok")
            print(f"    intent id  : {intent.id}")
            print(f"    status     : {intent.status}")
            print(f"    tx_type    : {intent.transaction_type}")
            print(f"    next_action: {intent.next_action}")
        except Exception as exc:  # noqa: BLE001
            _dump_error("collect", exc)


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        sys.exit(1)
