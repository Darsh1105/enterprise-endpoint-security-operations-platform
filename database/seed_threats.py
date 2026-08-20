import random

from database.connection import get_connection


THREATS = [
    (
        "Suspicious PowerShell Execution",
        "Execution",
        "T1059.001",
        "powershell.exe"
    ),
    (
        "Credential Dumping Attempt",
        "Credential Access",
        "T1003",
        "lsass.exe"
    ),
    (
        "Ransomware Activity",
        "Impact",
        "T1486",
        "encrypted_files"
    ),
    (
        "Malicious Script",
        "Execution",
        "T1059",
        "script.ps1"
    ),
    (
        "Encoded Command Execution",
        "Defense Evasion",
        "T1027",
        "powershell -enc"
    )
]


def seed_threats():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT device_id, risk_score
        FROM devices
        ORDER BY device_id
    """)

    devices = cursor.fetchall()

    total = 0

    for device in devices:

        risk = device["risk_score"]

        if risk <= 25:
            threat_count = random.randint(0, 1)

        elif risk <= 70:
            threat_count = random.randint(1, 2)

        else:
            threat_count = random.randint(2, 4)

        for _ in range(threat_count):

            threat = random.choice(THREATS)

            if risk <= 25:

                severity = "Low"
                status = "Resolved"

            elif risk <= 70:

                severity = "Medium"
                status = "Monitoring"

            else:

                severity = "High"
                status = "Active"

            cursor.execute("""

            INSERT INTO endpoint_threats(

                device_id,
                threat_name,
                severity,
                status,
                detection_source,
                mitre_technique,
                ioc,
                detected_time,
                description,
                recommended_action

            )

            VALUES(

                ?,
                ?,
                ?,
                ?,
                'Microsoft Defender',
                ?,
                ?,
                datetime('now'),
                ?,
                ?

            )

            """,

            (

                device["device_id"],
                threat[0],
                severity,
                status,
                threat[2],
                threat[3],
                f"{threat[0]} detected by Microsoft Defender.",
                "Investigate endpoint and run full antivirus scan."

            ))

            total += 1

    conn.commit()
    conn.close()

    print(f"{total} threats created successfully.")


if __name__ == "__main__":
    seed_threats()