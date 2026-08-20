import sqlite3
from pathlib import Path

# Database path
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "eesop.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def initialize_database():
    """Create the database and all tables from schema.sql"""
    print(DATABASE_PATH)
    conn = sqlite3.connect(DATABASE_PATH)

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = f.read()

    conn.executescript(schema)

    conn.commit()
    conn.close()

    print("EESOP Database created successfully!")


if __name__ == "__main__":
    initialize_database()