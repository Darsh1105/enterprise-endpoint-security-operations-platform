from database.connection import get_connection


def seed_security():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT device_id, risk_score
        FROM devices
        WHERE is_active = 1
    """)

    devices = cursor.fetchall()

    for device in devices:

        risk = device["risk_score"]

        if risk <= 25:

            defender_status = "Healthy"
            crowdstrike_status = "Connected"
            bitlocker_status = "Encrypted"
            realtime = "Enabled"
            tamper = "Enabled"
            firewall = "Enabled"
            tpm = "Ready"
            compliance = "Compliant"
            secure_boot = "Enabled"

        elif risk <= 70:

            defender_status = "Healthy"
            crowdstrike_status = "Connected"
            bitlocker_status = "Encrypted"
            realtime = "Enabled"
            tamper = "Enabled"
            firewall = "Enabled"
            tpm = "Ready"
            compliance = "Warning"
            secure_boot = "Enabled"

        else:

            defender_status = "Disabled"
            crowdstrike_status = "Offline"
            bitlocker_status = "Suspended"
            realtime = "Disabled"
            tamper = "Disabled"
            firewall = "Enabled"
            tpm = "Not Ready"
            compliance = "Non-Compliant"
            secure_boot = "Disabled"

        cursor.execute("""

        INSERT INTO endpoint_security_status(

            device_id,

            defender_status,
            defender_engine_version,
            defender_platform_version,
            defender_signature_version,
            defender_last_scan,

            realtime_protection,
            tamper_protection,

            crowdstrike_status,
            crowdstrike_sensor_version,
            crowdstrike_policy,
            crowdstrike_last_checkin,

            bitlocker_status,
            encryption_method,
            recovery_key_available,

            firewall_status,
            firewall_profile,

            tpm_status,
            tpm_version,

            secure_boot,

            compliance_status,
            last_sync

        )

        VALUES(

            ?,

            ?,
            '1.1.25070.3',
            '4.18.25060.7',
            '1.435.1200.0',
            datetime('now'),

            ?,
            ?,

            ?,
            '7.18.19234',
            'Windows Workstations',
            datetime('now'),

            ?,
            'XTS-AES 256',
            'Available',

            ?,
            'Domain, Private, Public',

            ?,
            '2.0',

            ?,

            ?,
            datetime('now')

        )

        """, (

            device["device_id"],

            defender_status,

            realtime,
            tamper,

            crowdstrike_status,

            bitlocker_status,

            firewall,

            tpm,

            secure_boot,

            compliance

        ))

    conn.commit()
    conn.close()

    print(f"{len(devices)} security profiles created.")


if __name__ == "__main__":
    seed_security()