from database.connection import get_connection


def create_remediation_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # ==================================================
    # Script Library
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS remediation_scripts (

            script_id INTEGER PRIMARY KEY AUTOINCREMENT,

            script_name TEXT NOT NULL,

            script_category TEXT NOT NULL,

            tool_name TEXT NOT NULL,

            script_type TEXT NOT NULL,

            version TEXT NOT NULL,

            purpose TEXT NOT NULL,

            risk_level TEXT NOT NULL,

            approval_required TEXT NOT NULL DEFAULT 'Yes',

            script_status TEXT NOT NULL DEFAULT 'Active',

            created_by TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # ==================================================
    # Script Deployment
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS script_deployments (

            deployment_id INTEGER PRIMARY KEY AUTOINCREMENT,

            script_id INTEGER NOT NULL,

            device_id INTEGER NOT NULL,

            requested_by TEXT NOT NULL,

            requested_time TEXT DEFAULT CURRENT_TIMESTAMP,

            approval_status TEXT NOT NULL DEFAULT 'Pending',

            deployment_status TEXT NOT NULL DEFAULT 'Not Deployed',

            execution_status TEXT NOT NULL DEFAULT 'Not Executed',

            execution_result TEXT,

            validation_status TEXT NOT NULL DEFAULT 'Pending',

            completed_time TEXT,

            remarks TEXT,

            FOREIGN KEY (script_id)
                REFERENCES remediation_scripts(script_id),

            FOREIGN KEY (device_id)
                REFERENCES devices(device_id)

        )
    """)

    conn.commit()
    conn.close()

    print(
        "Remediation tables created successfully."
    )


if __name__ == "__main__":
    create_remediation_tables()