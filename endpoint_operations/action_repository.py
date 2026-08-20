from database.connection import get_connection


def get_actions(device_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM endpoint_actions
        WHERE device_id = ?
        ORDER BY requested_time DESC
    """, (device_id,))

    actions = cursor.fetchall()

    conn.close()

    return actions