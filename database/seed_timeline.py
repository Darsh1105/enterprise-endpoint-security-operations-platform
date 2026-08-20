import random

from database.connection import get_connection


HEALTHY_EVENTS = [
    "User Login",
    "Microsoft Teams Started",
    "Outlook Opened",
    "Chrome Browser Started",
    "Windows Defender Quick Scan",
    "Intune Policy Sync",
    "User Logoff"
]

WARNING_EVENTS = [
    "User Login",
    "PowerShell Executed",
    "USB Device Connected",
    "Defender Warning",
    "Application Installed",
    "Policy Sync",
    "User Logoff"
]

CRITICAL_EVENTS = [
    "User Login",
    "PowerShell Executed",
    "Suspicious Script Detected",
    "Microsoft Defender Alert",
    "CrowdStrike Detection",
    "Threat Detected",
    "Incident Created",
    "Endpoint Isolation",
    "Engineering Investigation",
    "User Logoff"
]


def get_severity(risk):

    if risk <= 25:
        return "Informational"

    elif risk <= 70:
        return "Medium"

    return "High"


def seed_timeline():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            device_id,
            risk_score
        FROM devices
        WHERE is_active = 1
        ORDER BY device_id
    """)

    devices = cursor.fetchall()

    total_events = 0

    for device in devices:

        risk = device["risk_score"]

        if risk <= 25:

            events = random.sample(
                HEALTHY_EVENTS,
                random.randint(5, 7)
            )

        elif risk <= 70:

            events = random.sample(
                WARNING_EVENTS,
                random.randint(6, 7)
            )

        else:

            events = random.sample(
                CRITICAL_EVENTS,
                random.randint(8, 10)
            )

        for index, event in enumerate(events):

            cursor.execute("""

                INSERT INTO endpoint_timeline(

                    device_id,
                    event_time,
                    event_type,
                    event_category,
                    event_source,
                    severity,
                    description,
                    performed_by

                )

                VALUES(

                    ?,
                    datetime('now', ?),
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?

                )

            """, (

                device["device_id"],
                f"-{index * 10} minutes",
                event,
                "Endpoint Activity",
                "EESOP Simulator",
                get_severity(risk),
                event,
                "SYSTEM"

            ))

            total_events += 1

    conn.commit()
    conn.close()

    print(f"{total_events} timeline events created successfully.")


if __name__ == "__main__":
    seed_timeline()