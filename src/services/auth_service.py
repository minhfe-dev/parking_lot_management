from data.connect_database import get_connection

def login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT Role FROM TaiKhoan WHERE Username=%s AND Password=%s",
            (username, password)
        )
        result = cursor.fetchone()
        return result
    finally:
        conn.close()