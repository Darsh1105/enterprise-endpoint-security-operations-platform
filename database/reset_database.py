from database.connection import get_connection


TABLES = [

    "endpoint_actions",
    "endpoint_engineering",
    "endpoint_threats",
    "endpoint_incidents",
    "endpoint_timeline",
    "endpoint_security_status",
    "devices"

]


def reset_database():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = OFF")

    for table in TABLES:

        cursor.execute(f"DELETE FROM {table}")

        cursor.execute(
            f"DELETE FROM sqlite_sequence WHERE name='{table}'"
        )

    cursor.execute("PRAGMA foreign_keys = ON")

    conn.commit()

    conn.close()

    print("Database reset completed successfully.")


if __name__ == "__main__":
    reset_database()