from database.connection import get_connection


def get_engineering_activities(device_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM endpoint_engineering
        WHERE device_id = ?
        ORDER BY started_time DESC
    """, (device_id,))

    activities = cursor.fetchall()

    conn.close()

    return activities