from datetime import datetime

from data.connect_database import get_connection

# Mặc định: 3 ca × 8 giờ trong ngày (00–08, 08–16, 16–24)
DEFAULT_SHIFT1_MOTOR = 3000
DEFAULT_SHIFT1_CAR = 10000
DEFAULT_SHIFT2_MOTOR = 5000
DEFAULT_SHIFT2_CAR = 15000
DEFAULT_SHIFT3_MOTOR = 10000
DEFAULT_SHIFT3_CAR = 20000


def _table_exists(cursor, name: str) -> bool:
    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.tables "
        "WHERE table_schema = DATABASE() AND table_name = %s",
        (name,),
    )
    return cursor.fetchone()[0] > 0


def _column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.columns "
        "WHERE table_schema = DATABASE() AND table_name = %s AND column_name = %s",
        (table, column),
    )
    return cursor.fetchone()[0] > 0


def _ensure_pricing_schema(cursor):
    if not _table_exists(cursor, "pricing_config"):
        cursor.execute(
            """
            CREATE TABLE pricing_config (
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                shift1_motor INT NOT NULL DEFAULT %s,
                shift1_car INT NOT NULL DEFAULT %s,
                shift2_motor INT NOT NULL DEFAULT %s,
                shift2_car INT NOT NULL DEFAULT %s,
                shift3_motor INT NOT NULL DEFAULT %s,
                shift3_car INT NOT NULL DEFAULT %s,
                month_motor INT NOT NULL DEFAULT 0,
                month_car INT NOT NULL DEFAULT 0,
                day_motor INT NOT NULL DEFAULT %s,
                day_car INT NOT NULL DEFAULT %s
            )
            """,
            (
                DEFAULT_SHIFT1_MOTOR,
                DEFAULT_SHIFT1_CAR,
                DEFAULT_SHIFT2_MOTOR,
                DEFAULT_SHIFT2_CAR,
                DEFAULT_SHIFT3_MOTOR,
                DEFAULT_SHIFT3_CAR,
                DEFAULT_SHIFT1_MOTOR,
                DEFAULT_SHIFT1_CAR,
            ),
        )
        cursor.execute("INSERT INTO pricing_config () VALUES ()")
        return

    additions = [
        ("shift1_motor", f"INT NOT NULL DEFAULT {DEFAULT_SHIFT1_MOTOR}"),
        ("shift1_car", f"INT NOT NULL DEFAULT {DEFAULT_SHIFT1_CAR}"),
        ("shift2_motor", f"INT NOT NULL DEFAULT {DEFAULT_SHIFT2_MOTOR}"),
        ("shift2_car", f"INT NOT NULL DEFAULT {DEFAULT_SHIFT2_CAR}"),
        ("shift3_motor", f"INT NOT NULL DEFAULT {DEFAULT_SHIFT3_MOTOR}"),
        ("shift3_car", f"INT NOT NULL DEFAULT {DEFAULT_SHIFT3_CAR}"),
        ("month_motor", "INT NOT NULL DEFAULT 0"),
        ("month_car", "INT NOT NULL DEFAULT 0"),
        ("day_motor", f"INT NOT NULL DEFAULT {DEFAULT_SHIFT1_MOTOR}"),
        ("day_car", f"INT NOT NULL DEFAULT {DEFAULT_SHIFT1_CAR}"),
    ]
    for col, ddl in additions:
        if not _column_exists(cursor, "pricing_config", col):
            cursor.execute(f"ALTER TABLE pricing_config ADD COLUMN {col} {ddl}")

    cursor.execute("SELECT COUNT(*) FROM pricing_config")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO pricing_config () VALUES ()")


def shift_index_from_time(entry_time) -> int:
    """Ca 1: 00:00–08:00, ca 2: 08:00–16:00, ca 3: 16:00–24:00."""
    if isinstance(entry_time, str):
        entry_time = datetime.strptime(str(entry_time)[:19], "%Y-%m-%d %H:%M:%S")
    h = entry_time.hour
    if h < 8:
        return 1
    if h < 16:
        return 2
    return 3


def get_current_prices():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        _ensure_pricing_schema(cursor)
        conn.commit()
        cursor.execute(
            """
            SELECT shift1_motor, shift1_car, shift2_motor, shift2_car,
                   shift3_motor, shift3_car, month_motor, month_car,
                   day_motor, day_car
            FROM pricing_config LIMIT 1
            """
        )
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT INTO pricing_config () VALUES ()")
            conn.commit()
            cursor.execute(
                """
                SELECT shift1_motor, shift1_car, shift2_motor, shift2_car,
                       shift3_motor, shift3_car, month_motor, month_car,
                       day_motor, day_car
                FROM pricing_config LIMIT 1
                """
            )
            row = cursor.fetchone()

        return {
            "shift1_motor": row[0],
            "shift1_car": row[1],
            "shift2_motor": row[2],
            "shift2_car": row[3],
            "shift3_motor": row[4],
            "shift3_car": row[5],
            "month_motor": row[6],
            "month_car": row[7],
            "day_motor": row[8],
            "day_car": row[9],
        }
    finally:
        conn.close()


_DEFAULT_SHIFT_FEES = (
    (DEFAULT_SHIFT1_MOTOR, DEFAULT_SHIFT1_CAR),
    (DEFAULT_SHIFT2_MOTOR, DEFAULT_SHIFT2_CAR),
    (DEFAULT_SHIFT3_MOTOR, DEFAULT_SHIFT3_CAR),
)


def get_exit_fee_day_ticket(vehicle_type: str, entry_time) -> int:
    """Phí vé ngày theo ca vào bãi (một lần/lượt)."""
    p = get_current_prices()
    si = shift_index_from_time(entry_time)
    dm, dc = _DEFAULT_SHIFT_FEES[si - 1]
    if vehicle_type == "Ô tô":
        return int(p.get(f"shift{si}_car", dc))
    return int(p.get(f"shift{si}_motor", dm))


def update_prices(prices: dict):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        _ensure_pricing_schema(cursor)
        conn.commit()
        cursor.execute("SELECT COUNT(*) FROM pricing_config")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO pricing_config () VALUES ()")
            conn.commit()
        cursor.execute(
            """
            UPDATE pricing_config SET
                shift1_motor = %s, shift1_car = %s,
                shift2_motor = %s, shift2_car = %s,
                shift3_motor = %s, shift3_car = %s,
                month_motor = %s, month_car = %s,
                day_motor = %s, day_car = %s
            """,
            (
                prices["shift1_motor"],
                prices["shift1_car"],
                prices["shift2_motor"],
                prices["shift2_car"],
                prices["shift3_motor"],
                prices["shift3_car"],
                prices["month_motor"],
                prices["month_car"],
                prices["shift1_motor"],
                prices["shift1_car"],
            ),
        )
        conn.commit()
        return True, "Cập nhật đơn giá thành công!"
    except Exception as e:
        return False, f"Lỗi cơ sở dữ liệu: {e}"
    finally:
        conn.close()
