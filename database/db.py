
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "exhibit_p.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
        connection.executescript(file.read())

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()
    print("EXHIBIT P database initialized successfully.")
