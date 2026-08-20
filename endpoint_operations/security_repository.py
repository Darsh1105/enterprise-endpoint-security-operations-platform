from database.connection import get_connection


def get_security_status(device_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM endpoint_security_status
        WHERE device_id = ?
    """, (device_id,))

    security = cursor.fetchone()

    conn.close()

    return security