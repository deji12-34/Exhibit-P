"""Exhibit P Week 3 demo: actual receipt OCR + existing synthetic ledger.

This is an isolated PoC server. No changes to the existing app.py, database,
verification engine, or teammate's homepage are required.
"""
from __future__ import annotations

import io
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent

SCENARIOS = {
    "altered": {
        "reference": "NG-DEMO-000242", "amount": "250000.00", "currency": "NGN",
        "merchant_id": "TEST-MERCHANT-002", "status_text": "SETTLED",
    },
    "matched": {
        "reference": "NG-DEMO-000242", "amount": "42500.00", "currency": "NGN",
        "merchant_id": "TEST-MERCHANT-002", "status_text": "SETTLED",
    },
    "pending": {
        "reference": "KE-DEMO-000243", "amount": "7500.00", "currency": "KES",
        "merchant_id": "TEST-MERCHANT-001", "status_text": "SETTLED",
    },
    "unknown": {
        "reference": "NG-DEMO-NOTFOUND", "amount": "15000.00", "currency": "NGN",
        "merchant_id": "TEST-MERCHANT-002", "status_text": "SETTLED",
    },
}


def create_synthetic_receipt(case: str) -> bytes:
    """Build a conspicuously fictional PNG to use for a genuine OCR demonstration."""
    from PIL import Image, ImageDraw, ImageFont

    if case not in SCENARIOS:
        raise ValueError("Unknown demo case")
    claim = SCENARIOS[case]
    im = Image.new("RGB", (1120, 850), "#ffffff")
    draw = ImageDraw.Draw(im)

    def load_font(size: int, bold=False):
        faces = (
            ["DejaVuSans-Bold.ttf", "arialbd.ttf"] if bold
            else ["DejaVuSans.ttf", "arial.ttf"]
        )
        for face in faces:
            try:
                return ImageFont.truetype(face, size)
            except OSError:
                pass
        return ImageFont.load_default()

    bold = load_font(34, True)
    normal = load_font(30)
    big = load_font(52, True)
    mini = load_font(23)

    draw.rectangle([0, 0, 1120, 150], fill="#0b2435")
    draw.text((70, 48), "EXHIBIT P - DEMO RECEIPT", font=bold, fill="white")
    draw.text((75, 193), "PAYMENT SUCCESSFUL", font=bold, fill="#126b52")
    draw.text((75, 275), f"Amount: {claim['currency']} {float(claim['amount']):,.2f}", font=big, fill="#142839")
    details = [
        f"Transaction Reference: {claim['reference']}",
        f"Merchant ID: {claim['merchant_id']}",
        f"Status: {claim['status_text']}",
        "Channel: EXHIBIT P SANDBOX",
    ]
    for i, line in enumerate(details):
        draw.text((75, 385 + i * 68), line, font=normal, fill="#1b3343")
    draw.rectangle([60, 719, 1060, 817], fill="#fff0da", outline="#b7792c", width=3)
    draw.text((85, 738), "SYNTHETIC TEST ONLY - NO REAL PAYMENT", font=mini, fill="#653d10")
    draw.text((85, 774), "Not valid evidence of settlement", font=mini, fill="#653d10")
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return buf.getvalue()


def get_demo_record(reference: str):
    """Read the existing synthetic ledger; do not infer payment from an image."""
    from database.db import get_connection
    connection = get_connection()
    try:
        found = connection.execute(
            "SELECT reference, amount_minor, currency, recipient_tag, status "
            "FROM transactions WHERE reference = ?", (reference,)
        ).fetchall()
        if len(found) != 1:
            return None
        row = found[0]
        return {
            "reference": row["reference"],
            "amount": f"{row['amount_minor'] / 100:.2f}",
            "currency": row["currency"],
            "merchant_id": row["recipient_tag"],
            "status": row["status"],
        }
    finally:
        connection.close()


def evaluate_image(image_bytes: bytes) -> dict:
    """Run real Tesseract OCR, then the team's ledger-verification engine."""
    from ocr.extractor import extract_receipt
    from verification.engine import verify_payment

    scan = extract_receipt(image_bytes)
    fields = scan["fields"]
    required = ("reference", "amount", "currency", "merchant_id")
    if not all(fields.get(k) for k in required):
        return {
            "fields": fields, "record": None, "decision": "INCOMPLETE",
            "action": "HOLD", "reason": "A required field could not be read reliably.",
            "warnings": scan["warnings"], "average_confidence": scan["average_confidence"],
        }
    from decimal import Decimal, InvalidOperation
    try:
        minor_amount = Decimal(fields["amount"]) * 100
        if not minor_amount.is_finite() or minor_amount <= 0 or minor_amount != minor_amount.to_integral_value():
            raise ValueError("Invalid amount")
    except (InvalidOperation, ValueError):
        return {"fields": fields, "record": None, "decision": "INCOMPLETE",
                "action": "HOLD", "reason": "OCR produced an invalid amount.",
                "warnings": scan["warnings"], "average_confidence": scan["average_confidence"]}

    record = get_demo_record(fields["reference"])
    result = verify_payment(
        fields["reference"], int(minor_amount), fields["currency"], fields["merchant_id"]
    )
    name = result["result"]
    decision = {
        "RECORD_MATCHED": ("RECORD MATCH", "PROVIDER CHECK REQUIRED", "Fields match the synthetic ledger, but funds are not independently confirmed."),
        "MISMATCH": ("MISMATCH", "HOLD", "The screenshot claims differ from the synthetic transaction record."),
        "NOT_SETTLED": ("NOT SETTLED", "HOLD", "The synthetic transaction status is not settled."),
        "UNVERIFIED": ("UNVERIFIED", "HOLD", "The transaction reference is absent or ambiguous in the synthetic ledger."),
    }.get(name, ("REVIEW", "HOLD", "No safe automatic conclusion is available."))
    return {
        "fields": fields, "record": record, "decision": decision[0],
        "action": decision[1], "reason": decision[2],
        "warnings": scan["warnings"], "average_confidence": scan["average_confidence"],
        "verification": result,
        "source": "Tesseract OCR + simulated SQLite ledger",
    }


def create_app():
    from flask import Flask, jsonify, request, send_file, send_from_directory
    from ocr.extractor import OCRUnavailableError, ReceiptImageError
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024

    @app.get("/")
    def homepage():
        return send_from_directory(BASE / "poc", "index.html")

    @app.get("/api/poc/health")
    def health():
        return jsonify({"ready": shutil.which("tesseract") is not None,
                        "provider": "synthetic-ledger-only", "bank_connected": False})

    @app.get("/api/poc/sample/<case>.png")
    def sample(case):
        if case not in SCENARIOS:
            return jsonify({"error": "Unknown case"}), 404
        return send_file(io.BytesIO(create_synthetic_receipt(case)), mimetype="image/png")

    @app.post("/api/poc/assess")
    def assess():
        try:
            if "receipt" in request.files:
                image = request.files["receipt"].read(5 * 1024 * 1024 + 1)
            else:
                case = (request.get_json(silent=True) or {}).get("case", "")
                if case not in SCENARIOS:
                    return jsonify({"error": "Choose a valid demo case."}), 400
                image = create_synthetic_receipt(case)
            return jsonify(evaluate_image(image))
        except (ReceiptImageError, OCRUnavailableError) as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            app.logger.exception("PoC OCR assessment failed")
            return jsonify({"error": "Demo engine unavailable. Check the seeded database and OCR setup."}), 503

    return app


if __name__ == "__main__":
    import sys
    if "--self-test" in sys.argv:
        from database.seed import seed_database
        seed_database()
        for key in SCENARIOS:
            result = evaluate_image(create_synthetic_receipt(key))
            print(key, result["fields"], "->", result["decision"], result["action"])
    else:
        create_app().run(host="127.0.0.1", port=5000, debug=False)