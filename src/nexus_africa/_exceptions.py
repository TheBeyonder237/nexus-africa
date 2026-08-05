"""Typed exception hierarchy mirroring Nexus error code families.

Every non-2xx API response is converted into one of these exceptions by
:func:`raise_for_response`. The concrete subclass is chosen from the error
``code`` prefix (``PM-``, ``TI-``, ``verif-``, ``gtw-``, ``GE-``, ``BAL-``,
``TS-``) or, failing that, from the HTTP status. Catch :class:`NexusError` to
handle everything, or a specific subclass to react to one family::

    from nexus_africa import IdempotencyConflict, TransactionIntentError

    try:
        client.intents.cash_in(...)
    except IdempotencyConflict as exc:
        intent = client.intents.get(exc.error_data["transactionIntentId"])
    except TransactionIntentError as exc:
        log.warning("intent rejected: %s", exc.message)
"""

from __future__ import annotations

from typing import Any


class NexusError(Exception):
    """Base for all Nexus API errors.

    Attributes:
        code:        Machine-readable error code (e.g. ``"PM-0004"``), or
                     ``"UNKNOWN"`` when the body carried none.
        message:     Human-readable error summary from the API.
        http_status: HTTP status code of the failing response.
        detail:      Optional longer explanation, when the API supplies one.
        error_data:  Raw ``errorData`` payload — useful extra context such as
                     the id of an already-existing resource.
    """

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
    """Parse an error body and raise the matching typed exception.

    Resolution order: the specific ``GE-0002`` idempotency conflict first,
    then each ``code`` prefix family, then a fallback on the HTTP status
    (401/403, 429, 5xx). Anything unrecognised raises a bare :class:`NexusError`.

    Args:
        body:        Decoded JSON error body (``code`` / ``message`` / ...).
        http_status: HTTP status code of the response.

    Raises:
        NexusError: Always — a subclass whenever the family can be identified.
    """
    # ``code`` may be absent or explicitly ``null`` (validation errors do this),
    # so coalesce to "UNKNOWN" rather than trusting the key's presence.
    code: str = body.get("code") or "UNKNOWN"
    # Nexus returns RFC 7807-style error bodies: the human-readable summary is
    # in ``title`` and field-level errors in ``fieldErrors``. Keep ``message`` /
    # ``errorData`` as fallbacks for any endpoint using the alternative keys.
    message: str = body.get("message") or body.get("title") or "Unknown error"
    detail: str | None = body.get("detail")
    error_data: dict[str, Any] = body.get("errorData") or {}
    if not error_data and body.get("fieldErrors"):
        field_errors = body["fieldErrors"]
        # ``fieldErrors`` may be a dict or a list; preserve either under a key.
        error_data = (
            field_errors if isinstance(field_errors, dict) else {"fieldErrors": field_errors}
        )

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
