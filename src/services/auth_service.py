from data.connect_database import get_connection

def login(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT role FROM users WHERE username=%s AND password=%s",
        (username, password)
    )

    result = cursor.fetchone()  # ('admin',) hoặc None

    conn.close()
    return result