from database.connection import get_connection


def create_response_action_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incident_response_actions (

            action_id INTEGER PRIMARY KEY AUTOINCREMENT,

            incident_id INTEGER NOT NULL,

            device_id INTEGER NOT NULL,

            action_type TEXT NOT NULL,

            action_name TEXT NOT NULL,

            tool_name TEXT NOT NULL,

            status TEXT NOT NULL DEFAULT 'Pending',

            requested_by TEXT NOT NULL,

            executed_by TEXT,

            result TEXT,

            remarks TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            executed_at TEXT,

            FOREIGN KEY (incident_id)
                REFERENCES incidents(incident_id),

            FOREIGN KEY (device_id)
                REFERENCES devices(device_id)

        )
    """)

    conn.commit()
    conn.close()

    print(
        "Incident response action table created successfully."
    )


if __name__ == "__main__":
    create_response_action_table()