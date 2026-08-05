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


# ---------------------------------------------------------------------------
# RFC 7807-style bodies (real Nexus shape: title / detail / fieldErrors)
# ---------------------------------------------------------------------------

def test_title_used_as_message_when_message_absent():
    # Real sandbox 403 body observed for an IP-allowlist rejection.
    body = {
        "code": "GE-0004",
        "title": "Ip not allowed",
        "detail": "Ip address 1.2.3.4 is not amongst allowed Ip address list",
        "fieldErrors": None,
    }
    with pytest.raises(GeneralError) as exc:
        raise_for_response(body, 403)
    assert exc.value.message == "Ip not allowed"
    assert "not amongst allowed" in exc.value.detail
    assert "Ip not allowed" in str(exc.value)


def test_message_wins_over_title_when_both_present():
    body = {"code": "PM-0005", "message": "explicit", "title": "generic"}
    with pytest.raises(PaymentMethodError) as exc:
        raise_for_response(body, 400)
    assert exc.value.message == "explicit"


def test_field_errors_preserved_in_error_data():
    body = {
        "code": "verif-1001",
        "title": "Validation failed",
        "fieldErrors": [{"field": "amount", "message": "must be positive"}],
    }
    with pytest.raises(VerificationError) as exc:
        raise_for_response(body, 400)
    assert exc.value.error_data == {
        "fieldErrors": [{"field": "amount", "message": "must be positive"}]
    }


def test_missing_message_and_title_falls_back():
    with pytest.raises(NexusError) as exc:
        raise_for_response({"code": "UNKNOWN_CODE"}, 400)
    assert exc.value.message == "Unknown error"


def test_null_code_does_not_crash():
    # Real sandbox 400 body for a missing-field validation error: code is null.
    body = {
        "code": None,
        "title": "Invalid data provided",
        "detail": None,
        "fieldErrors": [
            {"objectName": "createTransactionIntentInput",
             "fieldName": "currencyCode", "errorMessage": "must not be blank"},
        ],
    }
    with pytest.raises(NexusError) as exc:
        raise_for_response(body, 400)
    assert exc.value.code == "UNKNOWN"
    assert exc.value.message == "Invalid data provided"
    assert exc.value.error_data["fieldErrors"][0]["fieldName"] == "currencyCode"
