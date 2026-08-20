from database.connection import get_connection


def create_auth_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # ==================================================
    # Platform Users
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS platform_users (

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

    # ==================================================
    # Role Permissions
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS role_permissions (

            permission_id INTEGER PRIMARY KEY AUTOINCREMENT,

            role TEXT NOT NULL,

            permission TEXT NOT NULL,

            UNIQUE(role, permission)

        )
    """)

    conn.commit()
    conn.close()

    print(
        "Authentication tables created successfully."
    )


if __name__ == "__main__":
    create_auth_tables()