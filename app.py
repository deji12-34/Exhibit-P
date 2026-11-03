
from flask import Flask, render_template, request
from decimal import Decimal, InvalidOperation

from verification.engine import verify_payment

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html", result=None)


@app.route("/verify", methods=["POST"])
def verify():

    reference = request.form.get("reference", "").strip()
    amount = request.form.get("amount", "").strip()
    currency = request.form.get("currency", "").strip()
    merchant_id = request.form.get("merchant_id", "").strip()

    if not all([reference, amount, currency, merchant_id]):
        result = {
            "result": "INVALID_INPUT",
            "message": "All fields are required."
        }

        return render_template("index.html", result=result)

    try:
        decimal_amount = Decimal(amount)

        if not decimal_amount.is_finite() or decimal_amount <= 0:
            raise ValueError("Invalid amount")

        minor_amount = decimal_amount * 100

        if minor_amount != minor_amount.to_integral_value():
            raise ValueError("Amount has too many decimal places")

        amount_minor = int(minor_amount)

    except (InvalidOperation, ValueError):
        result = {
            "result": "INVALID_INPUT",
            "message": "Enter a valid positive amount with at most two decimal places."
        }

        return render_template("index.html", result=result)

    result = verify_payment(
        reference,
        amount_minor,
        currency,
        merchant_id
    )

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
