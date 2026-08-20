from database.connection import get_connection


SCRIPTS = [

    # ==================================================
    # BitLocker / Encryption
    # ==================================================

    {
        "script_name": "TPM Health Remediation",
        "script_category": "Encryption",
        "tool_name": "PowerShell",
        "script_type": "Remediation Script",
        "version": "1.0",
        "purpose": (
            "Check TPM readiness and remediate common "
            "TPM configuration issues affecting BitLocker."
        ),
        "risk_level": "Medium"
    },

    {
        "script_name": "BitLocker Recovery Key Escrow Check",
        "script_category": "Encryption",
        "tool_name": "PowerShell",
        "script_type": "Compliance Script",
        "version": "1.0",
        "purpose": (
            "Verify that the BitLocker recovery key "
            "is available in the enterprise recovery system."
        ),
        "risk_level": "Low"
    },

    # ==================================================
    # Microsoft Defender
    # ==================================================

    {
        "script_name": "Defender Security Intelligence Update",
        "script_category": "Defender",
        "tool_name": "Microsoft Defender",
        "script_type": "Security Update",
        "version": "1.0",
        "purpose": (
            "Trigger a Microsoft Defender security "
            "intelligence update."
        ),
        "risk_level": "Low"
    },

    {
        "script_name": "Microsoft Defender Quick Scan",
        "script_category": "Defender",
        "tool_name": "Microsoft Defender",
        "script_type": "Security Scan",
        "version": "1.0",
        "purpose": (
            "Run a targeted Defender quick scan "
            "to identify common endpoint threats."
        ),
        "risk_level": "Low"
    },

    {
        "script_name": "Microsoft Defender Full Scan",
        "script_category": "Defender",
        "tool_name": "Microsoft Defender",
        "script_type": "Security Scan",
        "version": "1.0",
        "purpose": (
            "Perform a full endpoint malware scan "
            "for deeper threat investigation."
        ),
        "risk_level": "Medium"
    },

    # ==================================================
    # CrowdStrike
    # ==================================================

    {
        "script_name": "CrowdStrike Agent Health Check",
        "script_category": "CrowdStrike",
        "tool_name": "CrowdStrike Falcon",
        "script_type": "Health Check",
        "version": "1.0",
        "purpose": (
            "Check CrowdStrike sensor service status "
            "and endpoint sensor health."
        ),
        "risk_level": "Low"
    },

    {
        "script_name": "CrowdStrike Agent Upgrade",
        "script_category": "CrowdStrike",
        "tool_name": "CrowdStrike Falcon",
        "script_type": "Agent Upgrade",
        "version": "1.0",
        "purpose": (
            "Upgrade the CrowdStrike Falcon sensor "
            "to the approved enterprise version."
        ),
        "risk_level": "Medium"
    },

    # ==================================================
    # Firewall
    # ==================================================

    {
        "script_name": "Windows Firewall Compliance Fix",
        "script_category": "Firewall",
        "tool_name": "PowerShell",
        "script_type": "Remediation Script",
        "version": "1.0",
        "purpose": (
            "Verify Windows Firewall profiles and "
            "remediate disabled firewall protection."
        ),
        "risk_level": "Medium"
    },

    # ==================================================
    # Threat Remediation
    # ==================================================

    {
        "script_name": "Suspicious PowerShell Remediation",
        "script_category": "Threat Remediation",
        "tool_name": "PowerShell",
        "script_type": "Threat Remediation",
        "version": "1.0",
        "purpose": (
            "Perform controlled remediation actions "
            "for suspicious PowerShell activity."
        ),
        "risk_level": "High"
    },

    {
        "script_name": "Windows Security Service Recovery",
        "script_category": "Endpoint Health",
        "tool_name": "PowerShell",
        "script_type": "Service Remediation",
        "version": "1.0",
        "purpose": (
            "Check and recover required Windows "
            "security services."
        ),
        "risk_level": "Medium"
    }
]


def seed_remediation_scripts():

    conn = get_connection()
    cursor = conn.cursor()

    # Prevent duplicate seed data
    cursor.execute("""
        SELECT COUNT(*)
        FROM remediation_scripts
    """)

    existing_count = cursor.fetchone()[0]

    if existing_count > 0:

        print(
            f"Script library already contains "
            f"{existing_count} scripts."
        )

        conn.close()

        return

    total = 0

    for script in SCRIPTS:

        cursor.execute("""
            INSERT INTO remediation_scripts (

                script_name,
                script_category,
                tool_name,
                script_type,
                version,
                purpose,
                risk_level,
                approval_required,
                script_status,
                created_by

            )

            VALUES (

                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                'Yes',
                'Active',
                'EESOP Security Engineering'

            )
        """, (

            script["script_name"],
            script["script_category"],
            script["tool_name"],
            script["script_type"],
            script["version"],
            script["purpose"],
            script["risk_level"]

        ))

        total += 1

    conn.commit()
    conn.close()

    print(
        f"{total} remediation scripts created successfully."
    )


if __name__ == "__main__":
    seed_remediation_scripts()