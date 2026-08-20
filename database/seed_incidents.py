import random

from database.connection import get_connection


INCIDENT_TITLES = [
    "Suspicious PowerShell Execution",
    "Credential Dumping Attempt",
    "Ransomware Activity",
    "USB Device Connected",
    "Encoded PowerShell Command",
    "Suspicious Process Execution"
]


def seed_incidents():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            device_id,
            risk_score
        FROM devices
        ORDER BY device_id
    """)

    devices = cursor.fetchall()

    incident_number = 1
    total = 0

    for device in devices:

        risk = device["risk_score"]

        if risk <= 25:
            incident_count = 0

        elif risk <= 70:
            incident_count = random.randint(0, 1)

        else:
            incident_count = random.randint(1, 2)

        for _ in range(incident_count):

            title = random.choice(INCIDENT_TITLES)

            if risk <= 70:
                severity = "Medium"
                status = "Monitoring"
                sla = "Within SLA"

            else:
                severity = "High"
                status = "Open"
                sla = "Within SLA"

            detection_source = random.choice([
                "Microsoft Defender",
                "CrowdStrike Falcon"
            ])

            cursor.execute("""

                INSERT INTO endpoint_incidents(

                    device_id,
                    incident_number,
                    title,
                    severity,
                    status,
                    detection_source,
                    assigned_to,
                    sla_status,
                    created_time,
                    updated_time,
                    description

                )

                VALUES(

                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    datetime('now'),
                    datetime('now'),
                    ?

                )

            """, (

                device["device_id"],
                f"INC{incident_number:06}",
                title,
                severity,
                status,
                detection_source,
                "Darshit Goyal",
                sla,
                f"{title} detected and requires investigation."

            ))

            incident_number += 1
            total += 1

    conn.commit()
    conn.close()

    print(f"{total} incidents created successfully.")


if __name__ == "__main__":
    seed_incidents()