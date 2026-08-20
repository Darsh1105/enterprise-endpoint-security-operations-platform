from endpoint_operations.remediation_repository import (
    get_all_scripts,
    get_all_deployments,
    create_deployment,
    approve_deployment,
    execute_deployment,
    validate_deployment
)

from database.connection import get_connection


# ==================================================
# Load Script Library
# ==================================================

def load_scripts():

    return get_all_scripts()


# ==================================================
# Load Deployments
# ==================================================

def load_deployments():

    return get_all_deployments()


# ==================================================
# Request Deployment
# ==================================================

def request_deployment(
    script_id,
    device_id,
    requested_by="Security Analyst",
    remarks=""
):

    return create_deployment(
        script_id,
        device_id,
        requested_by,
        remarks
    )


# ==================================================
# Approve
# ==================================================

def approve_script_deployment(
    deployment_id,
    approved_by="Security Lead"
):

    approve_deployment(
        deployment_id,
        approved_by
    )


# ==================================================
# Execute
# ==================================================

def run_script_deployment(
    deployment_id
):

    execute_deployment(
        deployment_id
    )


# ==================================================
# Validate
# ==================================================

def validate_script_deployment(
    deployment_id
):

    validate_deployment(
        deployment_id
    )


# ==================================================
# Audit Timeline
# ==================================================

def create_remediation_timeline_event(
    device_id,
    event_type,
    description,
    severity="Informational",
    performed_by="Security Analyst"
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
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
            ?,
            'Remediation',
            'EESOP Remediation Engine',
            ?,
            ?,
            ?

        )
    """, (
        device_id,
        event_type,
        severity,
        description,
        performed_by
    ))

    conn.commit()
    conn.close()


# ==================================================
# Endpoint Action
# ==================================================

def create_remediation_action(
    device_id,
    action_name,
    tool_name,
    result,
    remarks,
    requested_by="Security Analyst"
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
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
            'Remediation',
            ?,
            datetime('now'),
            ?,
            'Completed',
            datetime('now'),
            ?,
            ?

        )
    """, (
        device_id,
        action_name,
        requested_by,
        tool_name,
        result,
        remarks
    ))

    conn.commit()

    action_id = cursor.lastrowid

    conn.close()

    return action_id