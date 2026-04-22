from data.connect_database import get_connection

def get_all():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, full_name, phone, position FROM employees")
        return cursor.fetchall()
    finally:
        conn.close()

def add(name, phone, position):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO employees (full_name, phone, position) VALUES (%s, %s, %s)",
            (name, phone, position)
        )
        conn.commit()
    finally:
        conn.close()

def update(staff_id, name, phone, position):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE employees SET full_name = %s, phone = %s, position = %s WHERE id = %s",
            (name, phone, position, staff_id)
        )
        conn.commit()
    finally:
        conn.close()

def delete(staff_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM employees WHERE id = %s", (staff_id,))
        conn.commit()
    finally:
        conn.close()

def search(keyword):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        like_keyword = f"%{keyword}%"
        cursor.execute(
            "SELECT id, full_name, phone, position FROM employees WHERE full_name LIKE %s OR phone LIKE %s",
            (like_keyword, like_keyword)
        )
        return cursor.fetchall()
    finally:
        conn.close()