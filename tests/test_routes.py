"""Regression tests for original homepage and isolated OCR page."""
import io
import pytest

pytest.importorskip("flask")
from app import app


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c


def test_home_preserves_original_verification_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Verify a Payment" in response.data
    assert b"Choose a payment receipt" not in response.data
    assert b"{% if result %}" not in response.data


def test_ocr_page_is_separate(client):
    response = client.get("/ocr")
    assert response.status_code == 200
    assert b"Scan a payment receipt" in response.data


def test_ocr_scan_prefills_review_form(client, monkeypatch):
    monkeypatch.setattr("ocr.routes.extract_receipt", lambda _content: {
        "fields": {
            "reference": "KE-DEMO-000241", "amount": "2500.00",
            "currency": "KES", "merchant_id": "TEST-MERCHANT-001",
            "status_text": "SETTLED",
        },
        "raw_text": "Synthetic receipt", "average_confidence": 91.5,
        "warnings": ["Receipt text is not settlement confirmation."],
    })
    response = client.post("/ocr", data={
        "receipt": (io.BytesIO(b"synthetic"), "receipt.png")
    }, content_type="multipart/form-data")
    assert response.status_code == 200
    assert b"KE-DEMO-000241" in response.data
    assert b"2500.00" in response.data
    assert b"not proof of payment" in response.data


def test_missing_receipt_has_clear_error(client):
    response = client.post("/ocr", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    assert b"Please choose a receipt image." in response.data
