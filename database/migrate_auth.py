import sqlite3

from config import DATABASE_PATH


def migrate_auth():

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Check existing columns
    cursor.execute(
        "PRAGMA table_info(platform_users)"
    )

    columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    # --------------------------------------------------
    # Already migrated
    # --------------------------------------------------

    if (
        "password_hash" in columns
        and "password_salt" in columns
    ):

        print(
            "Authentication schema is already updated."
        )

        conn.close()

        return

    # --------------------------------------------------
    # Rename old table
    # --------------------------------------------------

    cursor.execute(
        "ALTER TABLE platform_users "
        "RENAME TO platform_users_old"
    )

    # --------------------------------------------------
    # Create new table
    # --------------------------------------------------

    cursor.execute("""
        CREATE TABLE platform_users (

            user_id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT NOT NULL UNIQUE,

            password_hash TEXT NOT NULL,

            password_salt TEXT NOT NULL,

            display_name TEXT NOT NULL,

            role TEXT NOT NULL,

            is_active INTEGER NOT NULL DEFAULT 1,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # --------------------------------------------------
    # We intentionally do NOT copy old passwords.
    #
    # The old table contained development/demo
    # plaintext passwords. We will create fresh
    # securely hashed credentials with seed_auth.py.
    # --------------------------------------------------

    cursor.execute(
        "DROP TABLE platform_users_old"
    )

    conn.commit()
    conn.close()

    print(
        "Authentication schema migrated successfully."
    )


if __name__ == "__main__":
    migrate_auth()