from database.connection import get_connection


def get_timeline(device_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM endpoint_timeline
        WHERE device_id = ?
        ORDER BY event_time DESC
    """, (device_id,))

    timeline = cursor.fetchall()

    conn.close()

    return timeline