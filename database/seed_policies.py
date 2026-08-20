import random

from database.connection import get_connection


POLICIES = [

    # ==================================================
    # CrowdStrike
    # ==================================================

    {
        "policy_name": "CrowdStrike Prevention Policy",
        "policy_category": "CrowdStrike",
        "tool_name": "CrowdStrike Falcon",
        "policy_type": "Prevention Policy",
        "setting_name": "Prevention Mode",
        "current_value": "Enabled",
        "desired_value": "Enabled"
    },

    {
        "policy_name": "CrowdStrike Sensor Policy",
        "policy_category": "CrowdStrike",
        "tool_name": "CrowdStrike Falcon",
        "policy_type": "Sensor Policy",
        "setting_name": "Sensor Protection",
        "current_value": "Enabled",
        "desired_value": "Enabled"
    },

    # ==================================================
    # Microsoft Defender
    # ==================================================

    {
        "policy_name": "Microsoft Defender Antivirus",
        "policy_category": "Defender",
        "tool_name": "Microsoft Defender",
        "policy_type": "Antivirus Policy",
        "setting_name": "Real-time Protection",
        "current_value": "Enabled",
        "desired_value": "Enabled"
    },

    {
        "policy_name": "Microsoft Defender ASR",
        "policy_category": "Defender",
        "tool_name": "Microsoft Defender",
        "policy_type": "ASR Policy",
        "setting_name": "Block Credential Theft",
        "current_value": "Audit",
        "desired_value": "Block"
    },

    {
        "policy_name": "Microsoft Defender Tamper Protection",
        "policy_category": "Defender",
        "tool_name": "Microsoft Defender",
        "policy_type": "Security Policy",
        "setting_name": "Tamper Protection",
        "current_value": "Enabled",
        "desired_value": "Enabled"
    },

    # ==================================================
    # Encryption
    # ==================================================

    {
        "policy_name": "BitLocker Encryption Policy",
        "policy_category": "Encryption",
        "tool_name": "Microsoft Intune",
        "policy_type": "BitLocker Policy",
        "setting_name": "Encryption Method",
        "current_value": "XTS-AES 256",
        "desired_value": "XTS-AES 256"
    },

    {
        "policy_name": "BitLocker Recovery Key Policy",
        "policy_category": "Encryption",
        "tool_name": "Microsoft Intune",
        "policy_type": "Recovery Policy",
        "setting_name": "Recovery Key Availability",
        "current_value": "Available",
        "desired_value": "Available"
    },

    # ==================================================
    # Firewall
    # ==================================================

    {
        "policy_name": "Windows Firewall Policy",
        "policy_category": "Firewall",
        "tool_name": "Microsoft Defender",
        "policy_type": "Firewall Policy",
        "setting_name": "Firewall Protection",
        "current_value": "Enabled",
        "desired_value": "Enabled"
    },

    {
        "policy_name": "Windows Firewall Public Profile",
        "policy_category": "Firewall",
        "tool_name": "Microsoft Defender",
        "policy_type": "Firewall Policy",
        "setting_name": "Public Profile",
        "current_value": "Enabled",
        "desired_value": "Enabled"
    },

    # ==================================================
    # Custom
    # ==================================================

    {
        "policy_name": "TPM Remediation Script",
        "policy_category": "Custom",
        "tool_name": "PowerShell",
        "policy_type": "Remediation Script",
        "setting_name": "TPM Readiness",
        "current_value": "Compliant",
        "desired_value": "Compliant"
    },

    {
        "policy_name": "Endpoint Security Baseline",
        "policy_category": "Custom",
        "tool_name": "EESOP",
        "policy_type": "Security Baseline",
        "setting_name": "Endpoint Security Baseline",
        "current_value": "Applied",
        "desired_value": "Applied"
    }
]


def seed_policies():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT device_id, risk_score
        FROM devices
        WHERE is_active = 1
        ORDER BY device_id
    """)

    devices = cursor.fetchall()

    total = 0

    for device in devices:

        risk = device["risk_score"]

        # Every endpoint gets core security policies.
        selected_policies = random.sample(
            POLICIES,
            random.randint(6, 9)
        )

        for policy in selected_policies:

            # ------------------------------------------
            # Determine policy state
            # ------------------------------------------

            if risk >= 70:

                if random.random() < 0.35:

                    status = "Needs Review"
                    deployment_status = "Pending"
                    risk_level = "High"

                else:

                    status = "Assigned"
                    deployment_status = "Applied"
                    risk_level = "High"

            elif risk >= 40:

                if random.random() < 0.20:

                    status = "Needs Review"
                    deployment_status = "Pending"
                    risk_level = "Medium"

                else:

                    status = "Assigned"
                    deployment_status = "Applied"
                    risk_level = "Medium"

            else:

                status = "Assigned"
                deployment_status = "Applied"
                risk_level = "Low"

            cursor.execute("""
                INSERT INTO endpoint_policies (

                    device_id,
                    policy_name,
                    policy_category,
                    tool_name,
                    policy_type,
                    setting_name,
                    current_value,
                    desired_value,
                    status,
                    deployment_status,
                    risk_level,
                    last_updated,
                    updated_by,
                    change_reason

                )

                VALUES (

                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    datetime('now'),
                    'EESOP Policy Engine',
                    ?

                )
            """, (

                device["device_id"],
                policy["policy_name"],
                policy["policy_category"],
                policy["tool_name"],
                policy["policy_type"],
                policy["setting_name"],
                policy["current_value"],
                policy["desired_value"],
                status,
                deployment_status,
                risk_level,
                "Initial enterprise policy assignment"

            ))

            total += 1

    conn.commit()
    conn.close()

    print(
        f"{total} endpoint policies created successfully."
    )


if __name__ == "__main__":
    seed_policies()