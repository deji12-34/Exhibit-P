
CREATE TABLE IF NOT EXISTS transactions (
    txn_id TEXT PRIMARY KEY,
    country_code TEXT NOT NULL,
    provider_code TEXT NOT NULL,
    reference TEXT NOT NULL,
    amount_minor INTEGER NOT NULL,
    currency TEXT NOT NULL,
    recipient_tag TEXT NOT NULL,
    status TEXT NOT NULL,
    transaction_time_utc TEXT,
    sender_alias TEXT,

    UNIQUE(provider_code, reference)
);

CREATE TABLE IF NOT EXISTS fulfilments (
    fulfilment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT NOT NULL,
    order_id TEXT NOT NULL UNIQUE,
    fulfilled_at TEXT,

    UNIQUE(reference, order_id)
);
