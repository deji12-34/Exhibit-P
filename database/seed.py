
from database.db import get_connection, initialize_database

transactions = [
    (
        "TXN001", "KE", "DEMO-MFB",
        "KE-DEMO-000241", 250000,
        "KES", "TEST-MERCHANT-001",
        "SETTLED", "2026-11-03 08:30:00",
        "SENDER-A"
    ),
    (
        "TXN002", "NG", "DEMO-MFB",
        "NG-DEMO-000242", 4250000,
        "NGN", "TEST-MERCHANT-002",
        "SETTLED", "2026-11-03 09:00:00",
        "SENDER-B"
    ),
    (
        "TXN003", "KE", "DEMO-MFB",
        "KE-DEMO-000243", 750000,
        "KES", "TEST-MERCHANT-001",
        "PENDING", "2026-11-03 09:30:00",
        "SENDER-C"
    )
]


def seed_database():
    initialize_database()

    connection = get_connection()

    for transaction in transactions:
        connection.execute("""
            INSERT OR IGNORE INTO transactions (
                txn_id, country_code, provider_code,
                reference, amount_minor, currency,
                recipient_tag, status,
                transaction_time_utc, sender_alias
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, transaction)

    connection.commit()

    count = connection.execute(
        "SELECT COUNT(*) FROM transactions"
    ).fetchone()[0]

    connection.close()

    print(f"EXHIBIT P: {count} transaction records available.")


if __name__ == "__main__":
    seed_database()
