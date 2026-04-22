from data.connect_database import get_connection
from datetime import datetime
from src.services import gia_service


def process_entry(plate, img_path):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        time_in = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Kiểm tra vé tháng trong bảng monthly_passes
        cursor.execute("SELECT id, expiration_date, status FROM monthly_passes WHERE license_plate = %s", (plate,))
        ve_thang = cursor.fetchone()

        loai_ve = "Vé Ngày"
        if ve_thang and ve_thang[2] == 'Hoạt động':
            loai_ve = "Vé Tháng"

        # Ghi vào bảng vehicle_logs
        cursor.execute(
            "INSERT INTO vehicle_logs (license_plate, ticket_type, entry_time, entry_image, status) VALUES (%s, %s, %s, %s, 'Đang trong bãi')",
            (plate, loai_ve, time_in, img_path)
        )
        conn.commit()
        return True, f"Xe {plate} ({loai_ve}) đã vào bãi lúc {time_in}"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def process_exit(plate, img_path):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        time_out = datetime.now()
        time_out_str = time_out.strftime("%Y-%m-%d %H:%M:%S")

        # Tìm lượt vào trong vehicle_logs
        cursor.execute(
            "SELECT id, ticket_type, entry_time FROM vehicle_logs WHERE license_plate = %s AND status = 'Đang trong bãi'",
            (plate,)
        )
        luot_vao = cursor.fetchone()

        if not luot_vao:
            return False, "Không tìm thấy dữ liệu xe vào bãi!"

        id_gd, loai_ve, time_in = luot_vao
        thanh_tien = 0
        ghi_chu = "Hoàn thành"

        if loai_ve == "Vé Ngày":
            prices = gia_service.get_current_prices()
            if isinstance(time_in, datetime):
                t_in = time_in
            else:
                t_in = datetime.strptime(str(time_in)[:19], "%Y-%m-%d %H:%M:%S")

            hours = max(1, int((time_out - t_in).total_seconds() / 3600))
            thanh_tien = prices.get("day_motor", 0) * hours

        cursor.execute(
            "UPDATE vehicle_logs SET exit_time = %s, exit_image = %s, fee = %s, status = %s WHERE id = %s",
            (time_out_str, img_path, thanh_tien, ghi_chu, id_gd)
        )
        conn.commit()

        msg = f"Xe {plate} ra bãi lúc {time_out_str}."
        if loai_ve == "Vé Ngày":
            msg += f" Thu phí: {thanh_tien} VNĐ."

        return True, msg
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()