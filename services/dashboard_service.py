from database.connection import get_connection


# ==================================================
# Generic SQL Helper
# ==================================================

def execute_scalar(query, params=()):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(query, params)

    value = cursor.fetchone()[0]

    conn.close()

    return value if value is not None else 0


# ==================================================
# DEVICE KPIs
# ==================================================

def get_total_devices():

    return execute_scalar("""
        SELECT COUNT(*)
        FROM devices
        WHERE is_active = 1
    """)


def get_high_risk_devices():

    return execute_scalar("""
        SELECT COUNT(*)
        FROM devices
        WHERE risk_score >= 70
        AND is_active = 1
    """)


def get_average_risk_score():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT AVG(risk_score)
        FROM devices
        WHERE is_active = 1
    """)

    value = cursor.fetchone()[0]

    conn.close()

    if value is None:
        return 0

    return round(value)


# ==================================================
# DEFENDER COVERAGE
# ==================================================

def get_defender_coverage():

    total = get_total_devices()

    if total == 0:
        return 0

    healthy = execute_scalar("""
        SELECT COUNT(*)
        FROM endpoint_security_status
        WHERE defender_status = 'Healthy'
    """)

    return round((healthy / total) * 100, 1)


# ==================================================
# CROWDSTRIKE COVERAGE
# ==================================================

def get_crowdstrike_coverage():

    total = get_total_devices()

    if total == 0:
        return 0

    connected = execute_scalar("""
        SELECT COUNT(*)
        FROM endpoint_security_status
        WHERE crowdstrike_status = 'Connected'
    """)

    return round((connected / total) * 100, 1)


# ==================================================
# BITLOCKER COMPLIANCE
# ==================================================

def get_bitlocker_compliance():

    total = get_total_devices()

    if total == 0:
        return 0

    encrypted = execute_scalar("""
        SELECT COUNT(*)
        FROM endpoint_security_status
        WHERE bitlocker_status = 'Encrypted'
    """)

    return round((encrypted / total) * 100, 1)


# ==================================================
# FIREWALL COMPLIANCE
# ==================================================

def get_firewall_compliance():

    total = get_total_devices()

    if total == 0:
        return 0

    enabled = execute_scalar("""
        SELECT COUNT(*)
        FROM endpoint_security_status
        WHERE firewall_status = 'Enabled'
    """)

    return round((enabled / total) * 100, 1)


# ==================================================
# INCIDENT KPIs
# ==================================================

def get_open_incidents():

    return execute_scalar("""
        SELECT COUNT(*)
        FROM endpoint_incidents
        WHERE status = 'Open'
    """)


def get_sla_compliance():

    total = execute_scalar("""
        SELECT COUNT(*)
        FROM endpoint_incidents
    """)

    if total == 0:
        return 100

    within_sla = execute_scalar("""
        SELECT COUNT(*)
        FROM endpoint_incidents
        WHERE sla_status = 'Within SLA'
    """)

    return round((within_sla / total) * 100, 1)


# ==================================================
# RECENT INCIDENTS
# ==================================================

def get_recent_incidents(limit=5):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            i.incident_number,
            d.hostname,
            i.title,
            i.severity,
            i.status,
            i.detection_source
        FROM endpoint_incidents i
        INNER JOIN devices d
            ON d.device_id = i.device_id
        ORDER BY i.created_time DESC
        LIMIT ?
    """, (limit,))

    incidents = cursor.fetchall()

    conn.close()

    return incidents


# ==================================================
# RECENT TIMELINE ACTIVITIES
# ==================================================

def get_recent_timeline(limit=10):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            d.hostname,
            t.event_time,
            t.event_type,
            t.severity
        FROM endpoint_timeline t
        INNER JOIN devices d
            ON d.device_id = t.device_id
        ORDER BY t.event_time DESC
        LIMIT ?
    """, (limit,))

    activities = cursor.fetchall()

    conn.close()

    return activities


# ==================================================
# COMPLIANCE CHARTS
# ==================================================

def get_defender_chart():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            defender_status,
            COUNT(*)
        FROM endpoint_security_status
        GROUP BY defender_status
    """)

    data = cursor.fetchall()

    conn.close()

    return data


def get_bitlocker_chart():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            bitlocker_status,
            COUNT(*)
        FROM endpoint_security_status
        GROUP BY bitlocker_status
    """)

    data = cursor.fetchall()

    conn.close()

    return data


def get_risk_distribution():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            CASE
                WHEN risk_score <= 25 THEN 'Healthy'
                WHEN risk_score <= 70 THEN 'Warning'
                ELSE 'Critical'
            END AS risk_level,
            COUNT(*)
        FROM devices
        WHERE is_active = 1
        GROUP BY risk_level
        ORDER BY
            CASE risk_level
                WHEN 'Healthy' THEN 1
                WHEN 'Warning' THEN 2
                WHEN 'Critical' THEN 3
            END
    """)

    data = cursor.fetchall()

    conn.close()

    return data