from database.connection import get_connection


# ==================================================
# Threat Investigation Service
# ==================================================


def load_related_incidents(device_id, threat_name):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
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
        FROM endpoint_incidents
        WHERE device_id = ?
        AND (
            title = ?
            OR title LIKE ?
        )
        ORDER BY created_time DESC
        LIMIT 5
        """,
        (
            device_id,
            threat_name,
            f"%{threat_name.split()[0]}%"
        )
    )

    incidents = cursor.fetchall()

    conn.close()

    return incidents


def load_related_timeline(device_id, threat_name):

    conn = get_connection()
    cursor = conn.cursor()

    keyword = threat_name.split()[0]

    cursor.execute(
        """
        SELECT
            event_time,
            event_type,
            event_category,
            event_source,
            severity,
            description
        FROM endpoint_timeline
        WHERE device_id = ?
        AND (
            event_type LIKE ?
            OR description LIKE ?
        )
        ORDER BY event_time DESC
        LIMIT 10
        """,
        (
            device_id,
            f"%{keyword}%",
            f"%{keyword}%"
        )
    )

    events = cursor.fetchall()

    conn.close()

    return events


def load_endpoint_risk(device_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            hostname,
            operating_system,
            os_version,
            device_status,
            risk_score
        FROM devices
        WHERE device_id = ?
        """,
        (device_id,)
    )

    device = cursor.fetchone()

    conn.close()

    return device


def create_response_action(
    device_id,
    action_name,
    action_category,
    tool_name,
    requested_by="SOC Analyst"
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
            'Requested',
            NULL,
            'Action queued for simulation',
            'Created from Threat Investigation Workspace'
        )
        """,
        (
            device_id,
            action_name,
            action_category,
            requested_by,
            tool_name
        )
    )

    conn.commit()

    action_id = cursor.lastrowid

    conn.close()

    return action_id