from endpoint_operations.incident_repository import get_incidents

from endpoint_operations.remediation_service import (
    load_scripts,
    request_deployment,
    create_remediation_timeline_event,
    create_remediation_action
)

from database.connection import get_connection


# ==================================================
# Load Incidents
# ==================================================

def load_incidents(device_id):

    return get_incidents(device_id)


# ==================================================
# Load Remediation Scripts
# ==================================================

def load_remediation_scripts():

    return load_scripts()


# ==================================================
# Create Remediation Request From Incident
# ==================================================

def create_incident_remediation(
    incident,
    script_id,
    script_name,
    tool_name,
    requested_by="Security Analyst",
    remarks=""
):

    deployment_id = request_deployment(
        script_id=script_id,
        device_id=incident["device_id"],
        requested_by=requested_by,
        remarks=remarks
    )

    # ----------------------------------------------
    # Timeline
    # ----------------------------------------------

    create_remediation_timeline_event(
        device_id=incident["device_id"],
        event_type="Incident Remediation Requested",
        description=(
            f"Remediation script '{script_name}' "
            f"requested for incident "
            f"{incident['incident_number']} "
            f"on endpoint."
        ),
        severity=incident["severity"],
        performed_by=requested_by
    )

    # ----------------------------------------------
    # Endpoint Action
    # ----------------------------------------------

    create_remediation_action(
        device_id=incident["device_id"],
        action_name=(
            f"Incident Remediation - "
            f"{incident['incident_number']}"
        ),
        tool_name=tool_name,
        result="Remediation request created",
        remarks=(
            f"Incident: {incident['incident_number']} | "
            f"Script: {script_name} | "
            f"{remarks}"
        ),
        requested_by=requested_by
    )

    return deployment_id


# ==================================================
# Update Incident Status
# ==================================================

def update_incident_status(
    incident_id,
    status,
    assigned_to=None
):

    conn = get_connection()
    cursor = conn.cursor()

    if assigned_to:

        cursor.execute(
            """
            UPDATE endpoint_incidents

            SET
                status = ?,
                assigned_to = ?,
                updated_time = datetime('now')

            WHERE incident_id = ?
            """,
            (
                status,
                assigned_to,
                incident_id
            )
        )

    else:

        cursor.execute(
            """
            UPDATE endpoint_incidents

            SET
                status = ?,
                updated_time = datetime('now')

            WHERE incident_id = ?
            """,
            (
                status,
                incident_id
            )
        )

    conn.commit()
    conn.close()