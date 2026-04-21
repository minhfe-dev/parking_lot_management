from data.connect_database import get_connection

def get_all():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    rows = cursor.fetchall()
    conn.close()
    return rows


def add(name, phone, position):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO employees (name, phone, position) VALUES (%s,%s,%s)",
        (name, phone, position)
    )

    conn.commit()
    conn.close()


def update(staff_id, name, phone, position):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE employees SET name=%s, phone=%s, position=%s WHERE id=%s",
        (name, phone, position, staff_id)
    )

    conn.commit()
    conn.close()


def delete(staff_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM employees WHERE id=%s", (staff_id,))
    conn.commit()
    conn.close()


def search(keyword):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM employees WHERE name LIKE %s",
        (f"%{keyword}%",)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows