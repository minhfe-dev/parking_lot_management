from data.connect_database import get_connection

def get_revenue_summary(start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT SUM(ThanhTien) FROM LichSu WHERE ThoiGianRa >= %s AND ThoiGianRa <= %s AND TrangThai != 'Đang trong bãi'",
            (start_date, end_date)
        )
        result = cursor.fetchone()
        return result[0] if result and result[0] else 0
    finally:
        conn.close()