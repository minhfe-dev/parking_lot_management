from data.connect_database import get_connection

def get_all():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.id, u.username, u.role, e.name, u.employee_id
        FROM users u
        LEFT JOIN employees e ON u.employee_id = e.id
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_employees():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM employees")
    rows = cursor.fetchall()

    conn.close()
    return rows


def add(username, password, role, emp_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (username, password, role, employee_id) VALUES (%s,%s,%s,%s)",
        (username, password, role, emp_id)
    )

    conn.commit()
    conn.close()


def delete(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    conn.commit()
    conn.close()