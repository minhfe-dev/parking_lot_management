from data.connect_database import get_connection


def get_current_prices():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT day_motor, day_car, month_motor, month_car FROM pricing_config LIMIT 1")
        row = cursor.fetchone()

        if row:
            return {
                "day_motor": row[0],
                "day_car": row[1],
                "month_motor": row[2],
                "month_car": row[3]
            }
        return {"day_motor": 0, "day_car": 0, "month_motor": 0, "month_car": 0}
    finally:
        conn.close()


def update_prices(prices):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE pricing_config SET day_motor = %s, day_car = %s, month_motor = %s, month_car = %s",
            (prices["day_motor"], prices["day_car"], prices["month_motor"], prices["month_car"])
        )
        conn.commit()
        return True, "Cập nhật đơn giá thành công!"
    except Exception as e:
        return False, f"Lỗi cơ sở dữ liệu: {e}"
    finally:
        conn.close()