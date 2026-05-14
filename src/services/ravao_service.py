from data.connect_database import get_connection
from datetime import datetime
import re

from src.services import gia_service


def _normalize_plate(plate):
    return re.sub(r"[^A-Za-z0-9]", "", (plate or "").upper())


def _has_vehicle_type_column(cursor):
    cursor.execute("SHOW COLUMNS FROM vehicle_logs LIKE 'vehicle_type'")
    return cursor.fetchone() is not None


def _ensure_vehicle_type_column(cursor):
    if _has_vehicle_type_column(cursor):
        return
    cursor.execute("ALTER TABLE vehicle_logs ADD COLUMN vehicle_type VARCHAR(20) NULL AFTER ticket_type")


def process_entry(plate, img_path, vehicle_type):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        plate = _normalize_plate(plate)
        if not plate:
            return False, "Biển số không hợp lệ!"

        time_in = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Kiểm tra vé tháng trong bảng monthly_passes
        cursor.execute(
            """
            SELECT id, expiration_date, status
            FROM monthly_passes
            WHERE UPPER(REPLACE(REPLACE(REPLACE(license_plate, '-', ''), ' ', ''), '.', '')) = %s
            """,
            (plate,)
        )
        ve_thang = cursor.fetchone()

        loai_ve = "Vé Ngày"
        if ve_thang and ve_thang[2] == 'Hoạt động':
            loai_ve = "Vé Tháng"

        if vehicle_type not in ("Xe máy", "Ô tô"):
            return False, "Loại xe không hợp lệ!"

        _ensure_vehicle_type_column(cursor)
        has_vehicle_type = _has_vehicle_type_column(cursor)

        # Ghi vào bảng vehicle_logs (tương thích cả DB cũ chưa có vehicle_type)
        if has_vehicle_type:
            cursor.execute(
                """
                INSERT INTO vehicle_logs
                (license_plate, ticket_type, vehicle_type, entry_time, entry_image, status)
                VALUES (%s, %s, %s, %s, %s, 'Đang trong bãi')
                """,
                (plate, loai_ve, vehicle_type, time_in, img_path)
            )
        else:
            cursor.execute(
                """
                INSERT INTO vehicle_logs
                (license_plate, ticket_type, entry_time, entry_image, status)
                VALUES (%s, %s, %s, %s, 'Đang trong bãi')
                """,
                (plate, loai_ve, time_in, img_path)
            )
        conn.commit()
        return True, f"{vehicle_type} biển số {plate} ({loai_ve}) đã vào bãi lúc {time_in}"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def process_exit(plate, img_path):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        plate = _normalize_plate(plate)
        if not plate:
            return False, "Biển số không hợp lệ!"

        time_out = datetime.now()
        time_out_str = time_out.strftime("%Y-%m-%d %H:%M:%S")

        _ensure_vehicle_type_column(cursor)
        has_vehicle_type = _has_vehicle_type_column(cursor)

        # Tìm lượt vào trong vehicle_logs
        if has_vehicle_type:
            cursor.execute(
                """
                SELECT id, ticket_type, vehicle_type, entry_time
                FROM vehicle_logs
                WHERE UPPER(REPLACE(REPLACE(REPLACE(license_plate, '-', ''), ' ', ''), '.', '')) = %s
                  AND status = 'Đang trong bãi'
                ORDER BY entry_time DESC
                LIMIT 1
                """,
                (plate,)
            )
        else:
            cursor.execute(
                """
                SELECT id, ticket_type, entry_time
                FROM vehicle_logs
                WHERE UPPER(REPLACE(REPLACE(REPLACE(license_plate, '-', ''), ' ', ''), '.', '')) = %s
                  AND status = 'Đang trong bãi'
                ORDER BY entry_time DESC
                LIMIT 1
                """,
                (plate,)
            )
        luot_vao = cursor.fetchone()

        if not luot_vao:
            return False, "Không tìm thấy dữ liệu xe vào bãi!"

        if has_vehicle_type:
            id_gd, loai_ve, vehicle_type, time_in = luot_vao
        else:
            id_gd, loai_ve, time_in = luot_vao
            vehicle_type = "Xe"
        thanh_tien = 0
        ghi_chu = "Hoàn thành"

        if loai_ve == "Vé Ngày":
            if isinstance(time_in, datetime):
                t_in = time_in
            else:
                t_in = datetime.strptime(str(time_in)[:19], "%Y-%m-%d %H:%M:%S")
            vt = vehicle_type if vehicle_type in ("Xe máy", "Ô tô") else "Xe máy"
            thanh_tien = gia_service.get_exit_fee_day_ticket(vt, t_in)

        cursor.execute(
            "UPDATE vehicle_logs SET exit_time = %s, exit_image = %s, fee = %s, status = %s WHERE id = %s",
            (time_out_str, img_path, thanh_tien, ghi_chu, id_gd)
        )
        conn.commit()

        if not vehicle_type:
            vehicle_type = "Xe"
        msg = f"{vehicle_type} biển số {plate} đã rời bãi lúc {time_out_str}."
        if loai_ve == "Vé Ngày":
            msg += f" Thu phí: {thanh_tien} VNĐ."

        return True, msg
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()