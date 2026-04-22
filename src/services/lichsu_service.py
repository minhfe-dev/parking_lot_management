from data.connect_database import get_connection

def get_all():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            SELECT id, license_plate, ticket_type, 
                   COALESCE((SELECT customer_name FROM monthly_passes WHERE monthly_passes.license_plate = vehicle_logs.license_plate LIMIT 1), '') AS customer_name,
                   entry_time, exit_time, 
                   CASE WHEN status = 'Đang trong bãi' THEN status ELSE CAST(fee AS CHAR) END AS status
            FROM vehicle_logs
            ORDER BY entry_time DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        conn.close()

def search(plate, name, t_from, t_to):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            SELECT id, license_plate, ticket_type, 
                   COALESCE((SELECT customer_name FROM monthly_passes WHERE monthly_passes.license_plate = vehicle_logs.license_plate LIMIT 1), '') AS customer_name,
                   entry_time, exit_time, 
                   CASE WHEN status = 'Đang trong bãi' THEN status ELSE CAST(fee AS CHAR) END AS status
            FROM vehicle_logs
            WHERE (license_plate LIKE %s)
              AND (entry_time >= %s AND entry_time <= %s)
        """
        cursor.execute(query, (f"%{plate}%", t_from, t_to))
        return cursor.fetchall()
    finally:
        conn.close()