from database.connection import get_connection


# ==================================================
# Endpoint Policies
# ==================================================

def get_policies(device_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            policy_id,
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
            change_reason,
            created_at
        FROM endpoint_policies
        WHERE device_id = ?
        ORDER BY policy_category, policy_name
        """,
        (device_id,)
    )

    policies = cursor.fetchall()

    conn.close()

    return policies


# ==================================================
# Enterprise - All Policies
# ==================================================

def get_all_policies():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            p.policy_id,
            p.device_id,
            d.hostname,
            p.policy_name,
            p.policy_category,
            p.tool_name,
            p.policy_type,
            p.setting_name,
            p.current_value,
            p.desired_value,
            p.status,
            p.deployment_status,
            p.risk_level,
            p.last_updated,
            p.updated_by,
            p.change_reason,
            p.created_at

        FROM endpoint_policies p

        INNER JOIN devices d
            ON p.device_id = d.device_id

        ORDER BY
            p.policy_category,
            d.hostname,
            p.policy_name
        """
    )

    policies = cursor.fetchall()

    conn.close()

    return policies


# ==================================================
# Get Single Policy
# ==================================================

def get_policy(policy_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            policy_id,
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
        FROM endpoint_policies
        WHERE policy_id = ?
        """,
        (policy_id,)
    )

    policy = cursor.fetchone()

    conn.close()

    return policy


# ==================================================
# Tune Policy
# ==================================================

def update_policy_tuning(
    policy_id,
    desired_value,
    change_reason,
    updated_by="Security Engineer"
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE endpoint_policies
        SET
            desired_value = ?,
            status = 'Needs Review',
            deployment_status = 'Pending',
            last_updated = datetime('now'),
            updated_by = ?,
            change_reason = ?
        WHERE policy_id = ?
        """,
        (
            desired_value,
            updated_by,
            change_reason,
            policy_id
        )
    )

    conn.commit()
    conn.close()


# ==================================================
# Deploy Policy
# ==================================================

def deploy_policy(
    policy_id,
    updated_by="Security Engineer"
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE endpoint_policies
        SET
            current_value = desired_value,
            status = 'Assigned',
            deployment_status = 'Applied',
            last_updated = datetime('now'),
            updated_by = ?
        WHERE policy_id = ?
        """,
        (
            updated_by,
            policy_id
        )
    )

    conn.commit()
    conn.close()


# ==================================================
# Validate Policy
# ==================================================

def validate_policy(
    policy_id,
    updated_by="Security Engineer"
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE endpoint_policies
        SET
            status = 'Validated',
            deployment_status = 'Applied',
            last_updated = datetime('now'),
            updated_by = ?
        WHERE policy_id = ?
        """,
        (
            updated_by,
            policy_id
        )
    )

    conn.commit()
    conn.close()