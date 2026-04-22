from data.connect_database import get_connection
from datetime import datetime
from dateutil.relativedelta import relativedelta


def get_all():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Đổi từ TheThang thành monthly_passes và các cột tương ứng
        cursor.execute(
            "SELECT id, customer_name, license_plate, vehicle_type, expiration_date, status FROM monthly_passes")
        return cursor.fetchall()
    finally:
        conn.close()


def add(name, plate, v_type, months):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        ngay_het_han = datetime.now() + relativedelta(months=months)
        ngay_het_han_str = ngay_het_han.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "INSERT INTO monthly_passes (customer_name, license_plate, vehicle_type, expiration_date, status) VALUES (%s, %s, %s, %s, 'Hoạt động')",
            (name, plate, v_type, ngay_het_han_str)
        )
        conn.commit()
        return True, "Đăng ký vé tháng thành công!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def extend(card_id, months):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT expiration_date FROM monthly_passes WHERE id = %s", (card_id,))
        current_date_row = cursor.fetchone()

        if not current_date_row:
            return False, "Không tìm thấy thẻ!"

        if isinstance(current_date_row[0], datetime):
            current_date = current_date_row[0]
        else:
            current_date = datetime.strptime(str(current_date_row[0])[:19], "%Y-%m-%d %H:%M:%S")

        start_date = datetime.now() if current_date < datetime.now() else current_date
        new_date = start_date + relativedelta(months=months)

        cursor.execute(
            "UPDATE monthly_passes SET expiration_date = %s, status = 'Hoạt động' WHERE id = %s",
            (new_date.strftime("%Y-%m-%d %H:%M:%S"), card_id)
        )
        conn.commit()
        return True, "Gia hạn thành công!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def cancel(card_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE monthly_passes SET status = 'Đã hủy' WHERE id = %s", (card_id,))
        conn.commit()
        return True, "Hủy thẻ thành công!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()