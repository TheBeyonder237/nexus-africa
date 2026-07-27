"""Tests for webhook signature verification."""

import hashlib
import hmac
import json
import time

import pytest

from nexus_africa._enums import WebhookEventType
from nexus_africa._webhook import parse_event, verify_and_parse, verify_signature

SECRET = "wh_test_secret"


def _make_signature(raw_body: bytes, timestamp: str) -> str:
    message = (timestamp + raw_body.decode()).encode()
    return hmac.new(SECRET.encode(), message, hashlib.sha512).hexdigest()


SAMPLE_BODY = json.dumps({
    "id": "event_abc123",
    "type": "transactionIntent.statusUpdated",
    "data": {
        "object": {
            "transactionIntentId": "intent_xyz",
            "newStatus": "SUCCESSFUL",
        }
    },
    "operatorDetails": {"operatorId": 9, "merchantKey": "mk_test"},
}).encode()


def test_verify_signature_valid():
    ts = str(int(time.time()))
    sig = _make_signature(SAMPLE_BODY, ts)
    assert verify_signature(SAMPLE_BODY, ts, sig, SECRET)


def test_verify_signature_wrong_secret():
    ts = str(int(time.time()))
    sig = _make_signature(SAMPLE_BODY, ts)
    assert not verify_signature(SAMPLE_BODY, ts, sig, "wrong_secret")


def test_verify_signature_tampered_body():
    ts = str(int(time.time()))
    sig = _make_signature(SAMPLE_BODY, ts)
    tampered = SAMPLE_BODY.replace(b"SUCCESSFUL", b"FAILED")
    assert not verify_signature(tampered, ts, sig, SECRET)


def test_parse_event():
    event = parse_event(SAMPLE_BODY)
    assert event.id == "event_abc123"
    assert event.type == WebhookEventType.TRANSACTION_INTENT_STATUS_UPDATED
    assert event.transaction_intent_id == "intent_xyz"
    assert event.new_status == "SUCCESSFUL"


def test_verify_and_parse_ok():
    ts = str(int(time.time()))
    sig = _make_signature(SAMPLE_BODY, ts)
    event = verify_and_parse(SAMPLE_BODY, ts, sig, SECRET)
    assert event.new_status == "SUCCESSFUL"


def test_verify_and_parse_invalid_signature():
    ts = str(int(time.time()))
    with pytest.raises(ValueError, match="Invalid webhook signature"):
        verify_and_parse(SAMPLE_BODY, ts, "bad_sig", SECRET)


def test_verify_and_parse_stale_timestamp():
    old_ts = str(int(time.time()) - 400)
    sig = _make_signature(SAMPLE_BODY, old_ts)
    with pytest.raises(ValueError, match="old"):
        verify_and_parse(SAMPLE_BODY, old_ts, sig, SECRET, max_age_seconds=300)
