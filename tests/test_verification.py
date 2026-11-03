
from verification.engine import verify_payment


def test_successful_payment():
    result = verify_payment(
        "KE-DEMO-000241",
        250000,
        "KES",
        "TEST-MERCHANT-001"
    )
    assert result["result"] == "RECORD_MATCHED"


def test_pending_payment():
    result = verify_payment(
        "KE-DEMO-000243",
        750000,
        "KES",
        "TEST-MERCHANT-001"
    )
    assert result["result"] == "NOT_SETTLED"


def test_unknown_reference():
    result = verify_payment(
        "UNKNOWN-000001",
        250000,
        "KES",
        "TEST-MERCHANT-001"
    )
    assert result["result"] == "UNVERIFIED"


def test_wrong_amount():
    result = verify_payment(
        "KE-DEMO-000241",
        300000,
        "KES",
        "TEST-MERCHANT-001"
    )
    assert result["result"] == "MISMATCH"


def test_wrong_merchant():
    result = verify_payment(
        "KE-DEMO-000241",
        250000,
        "KES",
        "TEST-MERCHANT-999"
    )
    assert result["result"] == "MISMATCH"


def test_wrong_currency():
    result = verify_payment(
        "KE-DEMO-000241",
        250000,
        "USD",
        "TEST-MERCHANT-001"
    )
    assert result["result"] == "MISMATCH"


def test_invalid_amount():
    result = verify_payment(
        "KE-DEMO-000241",
        "not-a-number",
        "KES",
        "TEST-MERCHANT-001"
    )
    assert result["result"] == "MISMATCH"
