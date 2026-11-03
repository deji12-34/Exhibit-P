
from database.db import get_connection


def verify_payment(reference, amount, currency, merchant_id):
    """
    Verify a payment against the EXHIBIT P SQLite transaction database.

    Amount is supplied in minor currency units.
    """

    try:
        amount_minor = int(amount)
    except (TypeError, ValueError):
        return {
            "result": "MISMATCH",
            "message": "Invalid payment amount"
        }

    connection = get_connection()

    try:
        transactions = connection.execute(
            """
            SELECT
                txn_id,
                reference,
                amount_minor,
                currency,
                recipient_tag,
                status
            FROM transactions
            WHERE reference = ?
            """,
            (reference,)
        ).fetchall()

    finally:
        connection.close()

    if not transactions:
        return {
            "result": "UNVERIFIED",
            "message": "Transaction reference not found"
        }

    # A reference appearing more than once is ambiguous.
    if len(transactions) > 1:
        return {
            "result": "UNVERIFIED",
            "message": "Multiple matching transaction records found"
        }

    transaction = transactions[0]

    if transaction["status"] != "SETTLED":
        return {
            "result": "NOT_SETTLED",
            "message": "Transaction is not settled"
        }

    if transaction["recipient_tag"] != merchant_id:
        return {
            "result": "MISMATCH",
            "message": "Merchant ID mismatch"
        }

    if transaction["currency"] != currency:
        return {
            "result": "MISMATCH",
            "message": "Currency mismatch"
        }

    if transaction["amount_minor"] != amount_minor:
        return {
            "result": "MISMATCH",
            "message": "Amount mismatch"
        }

    return {
        "result": "RECORD_MATCHED",
        "message": "Details match the simulated demo ledger. Confirm funds separately in the official merchant account."
    }
