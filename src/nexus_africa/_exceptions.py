"""Typed exception hierarchy mirroring Nexus error code families."""

from __future__ import annotations

from typing import Any


class NexusError(Exception):
    """Base for all Nexus API errors."""

    code: str
    message: str
    http_status: int
    detail: str | None
    error_data: dict[str, Any]

    def __init__(
        self,
        code: str,
        message: str,
        http_status: int,
        detail: str | None = None,
        error_data: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.http_status = http_status
        self.detail = detail
        self.error_data = error_data or {}
        super().__init__(f"[{code}] {message}" + (f" — {detail}" if detail else ""))


class AuthError(NexusError):
    """401 / 403 — invalid or missing credentials."""


class PaymentMethodError(NexusError):
    """PM-xxxx — payment method creation / lookup errors."""


class TransactionIntentError(NexusError):
    """TI-xxxx — transaction intent lifecycle errors."""


class VerificationError(NexusError):
    """verif-xxxx — pre-execution business validation errors."""


class GatewayError(NexusError):
    """gtw-xxxx — provider-side errors (Mobile Money, banks)."""


class GeneralError(NexusError):
    """GE-xxxx — cross-cutting errors (idempotence, etc.)."""


class BalanceError(NexusError):
    """BAL-xxxx — balance query errors."""


class SessionError(NexusError):
    """TS-xxxx — hosted payment session errors."""


class IdempotencyConflict(GeneralError):
    """GE-0002 — a transaction already exists for this idempotency key.

    Treat this as a success: the original transaction was created.
    Fetch its state with ``client.intents.get(id)``.
    """


class RateLimitError(NexusError):
    """429 — too many requests."""


class ServerError(NexusError):
    """5xx — Nexus server-side error."""


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def raise_for_response(body: dict[str, Any], http_status: int) -> None:
    """Parse an error body and raise the matching typed exception."""
    code: str = body.get("code", "UNKNOWN")
    message: str = body.get("message", "Unknown error")
    detail: str | None = body.get("detail")
    error_data: dict[str, Any] = body.get("errorData") or {}

    kwargs: dict[str, Any] = dict(
        code=code,
        message=message,
        http_status=http_status,
        detail=detail,
        error_data=error_data,
    )

    if code == "GE-0002":
        raise IdempotencyConflict(**kwargs)
    if code.startswith("PM-"):
        raise PaymentMethodError(**kwargs)
    if code.startswith("TI-"):
        raise TransactionIntentError(**kwargs)
    if code.startswith("verif-"):
        raise VerificationError(**kwargs)
    if code.startswith("gtw-"):
        raise GatewayError(**kwargs)
    if code.startswith("GE-"):
        raise GeneralError(**kwargs)
    if code.startswith("BAL-"):
        raise BalanceError(**kwargs)
    if code.startswith("TS-"):
        raise SessionError(**kwargs)
    if http_status in (401, 403):
        raise AuthError(**kwargs)
    if http_status == 429:
        raise RateLimitError(**kwargs)
    if http_status >= 500:
        raise ServerError(**kwargs)
    raise NexusError(**kwargs)
