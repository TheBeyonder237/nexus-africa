"""Tests for the exception hierarchy and raise_for_response factory."""

import pytest

from nexus_africa._exceptions import (
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
    raise_for_response,
)


def _body(code: str, msg: str = "error") -> dict:
    return {"code": code, "message": msg, "status": "ERROR"}


def test_pm_error():
    with pytest.raises(PaymentMethodError) as exc:
        raise_for_response(_body("PM-0005"), 400)
    assert exc.value.code == "PM-0005"


def test_ti_error():
    with pytest.raises(TransactionIntentError):
        raise_for_response(_body("TI-0014"), 400)


def test_verif_error():
    with pytest.raises(VerificationError):
        raise_for_response(_body("verif-1001"), 400)


def test_gateway_error():
    with pytest.raises(GatewayError):
        raise_for_response(_body("gtw-4004"), 400)


def test_idempotency_conflict():
    with pytest.raises(IdempotencyConflict) as exc:
        raise_for_response(_body("GE-0002", "Idempotency Key Already Exists"), 409)
    assert isinstance(exc.value, GeneralError)


def test_balance_error():
    with pytest.raises(BalanceError):
        raise_for_response(_body("BAL-0001"), 400)


def test_session_error():
    with pytest.raises(SessionError):
        raise_for_response(_body("TS-0001"), 404)


def test_auth_error():
    with pytest.raises(AuthError):
        raise_for_response(_body("ACCESS_DENIED"), 401)


def test_rate_limit():
    with pytest.raises(RateLimitError):
        raise_for_response(_body("RATE_LIMIT"), 429)


def test_server_error():
    with pytest.raises(ServerError):
        raise_for_response(_body("GATEWAY_UNAVAILABLE"), 500)


def test_generic_nexus_error():
    with pytest.raises(NexusError):
        raise_for_response(_body("UNKNOWN_CODE"), 400)


def test_exception_str():
    with pytest.raises(PaymentMethodError) as exc:
        raise_for_response(_body("PM-0005", "Payment method not found"), 400)
    assert "PM-0005" in str(exc.value)
    assert "Payment method not found" in str(exc.value)
