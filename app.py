"""Exhibit P demonstration web application: OCR + synthetic ledger verification."""
from decimal import Decimal, InvalidOperation

from flask import Flask, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge

from ocr.extractor import OCRUnavailableError, ReceiptImageError, extract_receipt
from verification.engine import verify_payment

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024


def view(result=None, scan=None, form_values=None):
    return render_template(
        "index.html", result=result, scan=scan, form_values=form_values or {}
    )


@app.route("/")
def home():
    return view()


@app.route("/scan", methods=["POST"])
def scan():
    upload = request.files.get("receipt")
    if upload is None:
        return view(scan={"error": "Choose a receipt image to scan."}), 400
    try:
        # Do not save uploaded receipts or log their contents.
        extracted = extract_receipt(upload.read(5 * 1024 * 1024 + 1))
    except (ReceiptImageError, OCRUnavailableError) as exc:
        return view(scan={"error": str(exc)}), 400
    return view(scan=extracted, form_values=extracted["fields"])


@app.errorhandler(RequestEntityTooLarge)
def too_large(_error):
    return view(scan={"error": "Upload is too large. Use a PNG or JPEG smaller than 5 MB."}), 413


@app.route("/verify", methods=["POST"])
def verify():
    form = {key: request.form.get(key, "").strip() for key in
            ("reference", "amount", "currency", "merchant_id")}
    if not all(form.values()):
        return view(
            result={"result": "INVALID_INPUT", "message": "All fields are required."},
            form_values=form
        ), 400
    try:
        decimal_amount = Decimal(form["amount"])
        if not decimal_amount.is_finite() or decimal_amount <= 0:
            raise ValueError("Invalid amount")
        minor_amount = decimal_amount * 100
        if minor_amount != minor_amount.to_integral_value():
            raise ValueError("Too many decimal places")
        amount_minor = int(minor_amount)
    except (InvalidOperation, ValueError):
        return view(
            result={"result": "INVALID_INPUT", "message": "Enter a positive amount with at most two decimal places."},
            form_values=form
        ), 400
    result = verify_payment(
        form["reference"], amount_minor, form["currency"], form["merchant_id"]
    )
    return view(result=result, form_values=form)


if __name__ == "__main__":
    app.run(debug=False)
