from database.connection import get_connection


# ==================================================
# Supported Response Actions
# ==================================================

RESPONSE_ACTIONS = [

    {
        "action_type": "Scan",
        "action_name": "Run Security Scan",
        "tool_name": "Microsoft Defender",
        "risk_level": "Low"
    },

    {
        "action_type": "Signature Update",
        "action_name": "Update Security Intelligence",
        "tool_name": "Microsoft Defender",
        "risk_level": "Low"
    },

    {
        "action_type": "Agent Operation",
        "action_name": "Restart Security Agent",
        "tool_name": "Endpoint Security Agent",
        "risk_level": "Medium"
    },

    {
        "action_type": "Agent Upgrade",
        "action_name": "Upgrade Security Agent",
        "tool_name": "Endpoint Security Platform",
        "risk_level": "Medium"
    },

    {
        "action_type": "Containment",
        "action_name": "Isolate Endpoint",
        "tool_name": "EDR",
        "risk_level": "High"
    },

    {
        "action_type": "Containment",
        "action_name": "Quarantine Suspicious File",
        "tool_name": "EDR",
        "risk_level": "High"
    },

    {
        "action_type": "Policy",
        "action_name": "Apply Security Policy",
        "tool_name": "Endpoint Security Platform",
        "risk_level": "Medium"
    },

    {
        "action_type": "Remediation",
        "action_name": "Launch Remediation",
        "tool_name": "EESOP Remediation Engine",
        "risk_level": "High"
    }
]


# ==================================================
# Load Available Response Actions
# ==================================================

def get_response_actions():

    return RESPONSE_ACTIONS


# ==================================================
# Timeline Severity
# ==================================================

def _get_severity(action_type):

    if action_type == "Containment":
        return "High"

    if action_type in [
        "Agent Operation",
        "Agent Upgrade",
        "Policy",
        "Remediation"
    ]:
        return "Medium"

    return "Informational"


# ==================================================
# Create Response Action
# ==================================================

def create_response_action(
    incident_id,
    device_id,
    action_type,
    action_name,
    tool_name,
    requested_by,
    remarks=""
):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # ------------------------------------------
        # Create response action
        # ------------------------------------------

        cursor.execute(
            """
            INSERT INTO incident_response_actions (

                incident_id,
                device_id,
                action_type,
                action_name,
                tool_name,
                status,
                requested_by,
                remarks

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                incident_id,
                device_id,
                action_type,
                action_name,
                tool_name,
                "Pending",
                requested_by,
                remarks
            )
        )

        action_id = cursor.lastrowid


        # ------------------------------------------
        # Create audit event
        # ------------------------------------------

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
                CURRENT_TIMESTAMP,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            (
                device_id,
                "Response Action Requested",
                "Incident Response",
                tool_name,
                _get_severity(action_type),
                (
                    f"Response action "
                    f"'{action_name}' requested "
                    f"for incident #{incident_id}."
                ),
                requested_by
            )
        )


        conn.commit()

        return action_id

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


# ==================================================
# Execute Response Action
# ==================================================

def execute_response_action(
    action_id,
    executed_by
):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # ------------------------------------------
        # Get action
        # ------------------------------------------

        cursor.execute(
            """
            SELECT
                action_id,
                incident_id,
                device_id,
                action_type,
                action_name,
                tool_name,
                status

            FROM incident_response_actions

            WHERE action_id = ?
            """,
            (action_id,)
        )

        action = cursor.fetchone()


        if action is None:

            return False, (
                "Response action not found."
            )


        # ------------------------------------------
        # Prevent duplicate execution
        # ------------------------------------------

        if action["status"] == "Completed":

            return False, (
                "Response action has already "
                "been executed."
            )


        # ------------------------------------------
        # Simulated execution
        # ------------------------------------------

        result = (
            f"Simulated execution successful: "
            f"{action['action_name']} performed "
            f"using {action['tool_name']}."
        )


        # ------------------------------------------
        # Update action
        # ------------------------------------------

        cursor.execute(
            """
            UPDATE incident_response_actions

            SET
                status = ?,
                executed_by = ?,
                result = ?,
                executed_at = CURRENT_TIMESTAMP

            WHERE action_id = ?
            """,
            (
                "Completed",
                executed_by,
                result,
                action_id
            )
        )


        # ------------------------------------------
        # Create execution audit event
        # ------------------------------------------

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
                CURRENT_TIMESTAMP,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            (
                action["device_id"],
                "Response Action Executed",
                "Incident Response",
                action["tool_name"],
                _get_severity(
                    action["action_type"]
                ),
                (
                    f"Response action "
                    f"'{action['action_name']}' "
                    f"executed for incident "
                    f"#{action['incident_id']}. "
                    f"Result: {result}"
                ),
                executed_by
            )
        )


        conn.commit()

        return True, result

    except Exception as error:

        conn.rollback()

        return False, (
            f"Response action execution failed: "
            f"{error}"
        )

    finally:

        conn.close()


# ==================================================
# Get Actions For Incident
# ==================================================

def get_incident_response_actions(
    incident_id
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            action_id,
            incident_id,
            device_id,
            action_type,
            action_name,
            tool_name,
            status,
            requested_by,
            executed_by,
            result,
            remarks,
            created_at,
            executed_at

        FROM incident_response_actions

        WHERE incident_id = ?

        ORDER BY created_at DESC
        """,
        (incident_id,)
    )

    actions = cursor.fetchall()

    conn.close()

    return actions


# ==================================================
# Get All Response Actions
# ==================================================

def get_all_response_actions():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            action_id,
            incident_id,
            device_id,
            action_type,
            action_name,
            tool_name,
            status,
            requested_by,
            executed_by,
            result,
            remarks,
            created_at,
            executed_at

        FROM incident_response_actions

        ORDER BY created_at DESC
        """
    )

    actions = cursor.fetchall()

    conn.close()

    return actions