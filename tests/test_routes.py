"""Web integration tests (run when Flask and Werkzeug are installed)."""
import io
import pytest

pytest.importorskip("flask")
from app import app


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def test_home_page_has_both_stages(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Scan receipt" in response.data
    assert b"Verify claimed payment" in response.data


def test_ocr_scan_prefills_editable_fields(client, monkeypatch):
    monkeypatch.setattr("app.extract_receipt", lambda _content: {
        "fields": {
            "reference": "KE-DEMO-000241", "amount": "2500.00",
            "currency": "KES", "merchant_id": "TEST-MERCHANT-001",
            "status_text": "SETTLED",
        },
        "raw_text": "Synthetic receipt", "average_confidence": 91.5,
        "warnings": ["Status is not proof of payment."],
    })
    response = client.post(
        "/scan", data={"receipt": (io.BytesIO(b"data"), "receipt.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert b"KE-DEMO-000241" in response.data
    assert b"2500.00" in response.data
    assert b"Nothing has been verified yet" in response.data


def test_missing_receipt_is_friendly_error(client):
    response = client.post("/scan", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    assert b"Choose a receipt image" in response.data


def test_invalid_amount(client):
    response = client.post("/verify", data={
        "reference": "SYNTHETIC-001", "amount": "NaN",
        "currency": "KES", "merchant_id": "DEMO",
    })
    assert response.status_code == 400
    assert b"INVALID INPUT" in response.data
