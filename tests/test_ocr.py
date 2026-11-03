"""Synthetic tests: no real customer receipts."""
import io

import pytest
from PIL import Image

from ocr.extractor import ReceiptImageError, open_receipt, parse_receipt_text


def test_parses_kenyan_example():
    sample = """Payment Successful
Transaction Reference: KE-DEMO-000241
Amount: KES 2,500.00
Merchant ID: TEST-MERCHANT-001
Status: SETTLED"""
    result = parse_receipt_text(sample)
    assert result["fields"] == {
        "reference": "KE-DEMO-000241",
        "amount": "2500.00",
        "currency": "KES",
        "merchant_id": "TEST-MERCHANT-001",
        "status_text": "SETTLED",
    }
    assert "settlement" in " ".join(result["warnings"]).lower()


def test_parses_nigerian_example():
    sample = """Transfer Receipt
Reference: NG-DEMO-000242
Amount: ₦42,500.00
Merchant ID: TEST-MERCHANT-002
Status: Successful"""
    result = parse_receipt_text(sample)
    assert result["fields"]["amount"] == "42500.00"
    assert result["fields"]["currency"] == "NGN"
    assert result["fields"]["reference"] == "NG-DEMO-000242"


def test_ambiguous_data_stays_empty():
    result = parse_receipt_text("Some screenshot with no payment information")
    assert result["fields"]["reference"] == ""
    assert result["fields"]["amount"] == ""
    assert len(result["warnings"]) >= 3


def test_rejects_non_image():
    with pytest.raises(ReceiptImageError):
        open_receipt(b"not a real receipt image")


def test_rejects_oversized_upload():
    with pytest.raises(ReceiptImageError):
        open_receipt(b"x" * (5 * 1024 * 1024 + 1))


def test_opens_valid_png_in_memory():
    buf = io.BytesIO()
    Image.new("RGB", (200, 90), color="white").save(buf, "PNG")
    out = open_receipt(buf.getvalue())
    assert out.size == (200, 90)
    assert out.mode == "RGB"
