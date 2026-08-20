from endpoint_operations.policy_repository import (
    get_policies,
    get_all_policies,
    get_policy,
    update_policy_tuning,
    deploy_policy,
    validate_policy
)

from database.connection import get_connection


# ==================================================
# Endpoint Policies
# ==================================================

def load_policies(device_id):

    return get_policies(device_id)


# ==================================================
# Enterprise Policies
# ==================================================

def load_all_policies():

    return get_all_policies()


# ==================================================
# Tune Policy
# ==================================================

def tune_policy(
    policy_id,
    desired_value,
    change_reason,
    updated_by="Security Engineer"
):

    update_policy_tuning(
        policy_id,
        desired_value,
        change_reason,
        updated_by
    )


# ==================================================
# Deploy Policy
# ==================================================

def apply_policy(
    policy_id,
    updated_by="Security Engineer"
):

    policy = get_policy(policy_id)

    if policy is None:
        return False, "Policy not found."

    if policy["status"] != "Needs Review":
        return (
            False,
            "Policy must be tuned before deployment."
        )

    deploy_policy(
        policy_id,
        updated_by
    )

    return (
        True,
        "Policy deployment simulated successfully."
    )


# ==================================================
# Validate Policy
# ==================================================

def validate_policy_change(
    policy_id,
    updated_by="Security Engineer"
):

    policy = get_policy(policy_id)

    if policy is None:
        return False, "Policy not found."

    if policy["deployment_status"] != "Applied":
        return (
            False,
            "Policy must be deployed before validation."
        )

    validate_policy(
        policy_id,
        updated_by
    )

    return (
        True,
        "Policy validation completed successfully."
    )


# ==================================================
# Timeline Audit
# ==================================================

def create_policy_timeline_event(
    device_id,
    event_type,
    description,
    severity="Informational",
    performed_by="Security Engineer"
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO endpoint_timeline (
            device_id,
            event_time,
            event_type,
            event_category,
            event_source,
            severity,
            description,
            performed_by
        )
        VALUES (
            ?,
            datetime('now'),
            'Policy Management',
            'Policy Management',
            'EESOP Policy Engine',
            ?,
            ?,
            ?
        )
        """,
        (
            device_id,
            severity,
            description,
            performed_by
        )
    )

    conn.commit()
    conn.close()


# ==================================================
# Endpoint Action Audit
# ==================================================

def create_policy_action(
    device_id,
    action_name,
    action_category,
    tool_name,
    result,
    remarks,
    requested_by="Security Engineer"
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO endpoint_actions (
            device_id,
            action_name,
            action_category,
            requested_by,
            requested_time,
            tool_name,
            status,
            completed_time,
            result,
            remarks
        )
        VALUES (
            ?,
            ?,
            ?,
            ?,
            datetime('now'),
            ?,
            'Completed',
            datetime('now'),
            ?,
            ?
        )
        """,
        (
            device_id,
            action_name,
            action_category,
            requested_by,
            tool_name,
            result,
            remarks
        )
    )

    conn.commit()

    action_id = cursor.lastrowid

    conn.close()

    return action_id