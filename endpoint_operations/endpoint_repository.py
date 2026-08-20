from database.connection import get_connection


def get_all_devices():
    """
    Returns all active devices.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM devices
        WHERE is_active = 1
        ORDER BY hostname
    """)

    devices = cursor.fetchall()

    conn.close()

    return devices


def get_endpoint_by_hostname(hostname):
    """
    Returns one endpoint by hostname.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM devices
        WHERE hostname = ?
    """, (hostname,))

    device = cursor.fetchone()

    conn.close()

    return device