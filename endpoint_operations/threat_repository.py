from database.connection import get_connection


def get_threats(device_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM endpoint_threats
        WHERE device_id = ?
        ORDER BY detected_time DESC
    """, (device_id,))

    threats = cursor.fetchall()

    conn.close()

    return threats