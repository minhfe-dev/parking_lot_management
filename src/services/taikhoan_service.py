from data.connect_database import get_connection

def get_all():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username, password, role, employee_id FROM users")
        return cursor.fetchall()
    finally:
        conn.close()

def get_employees():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Đổi từ NhanVien thành employees, ID_NV thành id, HoTen thành full_name
        cursor.execute("SELECT id, full_name FROM employees")
        return cursor.fetchall()
    finally:
        conn.close()

def add(username, password, role, id_nv):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role, employee_id) VALUES (%s, %s, %s, %s)",
            (username, password, role, id_nv)
        )
        conn.commit()
    finally:
        conn.close()

def delete(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
    finally:
        conn.close()