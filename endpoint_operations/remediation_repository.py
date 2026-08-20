from database.connection import get_connection


# ==================================================
# Script Library
# ==================================================

def get_all_scripts():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            script_id,
            script_name,
            script_category,
            tool_name,
            script_type,
            version,
            purpose,
            risk_level,
            approval_required,
            script_status,
            created_by,
            created_at
        FROM remediation_scripts
        WHERE script_status = 'Active'
        ORDER BY script_category, script_name
    """)

    scripts = cursor.fetchall()

    conn.close()

    return scripts


# ==================================================
# Script Deployments
# ==================================================

def get_all_deployments():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            sd.deployment_id,
            sd.script_id,
            rs.script_name,
            rs.script_category,
            rs.tool_name,
            sd.device_id,
            d.hostname,
            sd.requested_by,
            sd.requested_time,
            sd.approval_status,
            sd.deployment_status,
            sd.execution_status,
            sd.execution_result,
            sd.validation_status,
            sd.completed_time,
            sd.remarks

        FROM script_deployments sd

        INNER JOIN remediation_scripts rs
            ON sd.script_id = rs.script_id

        INNER JOIN devices d
            ON sd.device_id = d.device_id

        ORDER BY sd.requested_time DESC
    """)

    deployments = cursor.fetchall()

    conn.close()

    return deployments


# ==================================================
# Create Deployment Request
# ==================================================

def create_deployment(
    script_id,
    device_id,
    requested_by="Security Analyst",
    remarks=""
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO script_deployments (

            script_id,
            device_id,
            requested_by,
            approval_status,
            deployment_status,
            execution_status,
            validation_status,
            remarks

        )

        VALUES (

            ?,
            ?,
            ?,
            'Pending',
            'Not Deployed',
            'Not Executed',
            'Pending',
            ?

        )
    """, (
        script_id,
        device_id,
        requested_by,
        remarks
    ))

    conn.commit()

    deployment_id = cursor.lastrowid

    conn.close()

    return deployment_id


# ==================================================
# Approve Deployment
# ==================================================

def approve_deployment(
    deployment_id,
    approved_by="Security Lead"
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE script_deployments

        SET
            approval_status = 'Approved',
            remarks = ?

        WHERE deployment_id = ?
    """, (
        f"Approved by {approved_by}",
        deployment_id
    ))

    conn.commit()
    conn.close()


# ==================================================
# Execute Deployment
# ==================================================

def execute_deployment(
    deployment_id,
    result="Execution completed successfully"
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE script_deployments

        SET
            deployment_status = 'Deployed',
            execution_status = 'Completed',
            execution_result = ?,
            completed_time = datetime('now'),
            validation_status = 'Pending'

        WHERE deployment_id = ?
    """, (
        result,
        deployment_id
    ))

    conn.commit()
    conn.close()


# ==================================================
# Validate Deployment
# ==================================================

def validate_deployment(
    deployment_id,
    validation_result="Remediation validated successfully"
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE script_deployments

        SET
            validation_status = 'Validated',
            execution_result = ?

        WHERE deployment_id = ?
    """, (
        validation_result,
        deployment_id
    ))

    conn.commit()
    conn.close()