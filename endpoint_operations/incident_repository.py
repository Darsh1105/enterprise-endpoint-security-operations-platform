from database.connection import get_connection


def get_incidents(device_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM endpoint_incidents
        WHERE device_id = ?
        ORDER BY created_time DESC
    """, (device_id,))

    incidents = cursor.fetchall()

    conn.close()

    return incidents