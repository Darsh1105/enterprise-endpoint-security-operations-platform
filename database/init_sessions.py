from database.connection import get_connection


def create_session_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_sessions (

            session_id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            token_hash TEXT NOT NULL UNIQUE,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            expires_at TIMESTAMP NOT NULL,

            last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            is_active INTEGER DEFAULT 1,

            FOREIGN KEY (user_id)
                REFERENCES platform_users(user_id)

        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_auth_sessions_token
        ON auth_sessions(token_hash)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_auth_sessions_user
        ON auth_sessions(user_id)
    """)

    conn.commit()
    conn.close()

    print(
        "Authentication session table created successfully."
    )


if __name__ == "__main__":
    create_session_table()