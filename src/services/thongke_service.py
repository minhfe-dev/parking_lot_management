from datetime import datetime, timedelta

from data.connect_database import get_connection


def _sum_fee(cursor, start_time, end_time):
    cursor.execute(
        """
        SELECT COALESCE(SUM(fee), 0)
        FROM vehicle_logs
        WHERE exit_time >= %s
          AND exit_time <= %s
          AND status != 'Đang trong bãi'
        """,
        (start_time, end_time),
    )
    row = cursor.fetchone()
    return int(row[0] or 0)


def get_revenue_summary():
    now = datetime.now()
    day_start = datetime(now.year, now.month, now.day)
    week_start = day_start - timedelta(days=day_start.weekday())
    month_start = datetime(now.year, now.month, 1)

    conn = get_connection()
    cursor = conn.cursor()
    try:
        return {
            "day": _sum_fee(cursor, day_start, now),
            "week": _sum_fee(cursor, week_start, now),
            "month": _sum_fee(cursor, month_start, now),
        }
    finally:
        conn.close()


def get_vehicles_in_lot():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT license_plate,
                   COALESCE(vehicle_type, 'Xe'),
                   ticket_type,
                   entry_time
            FROM vehicle_logs
            WHERE status = 'Đang trong bãi'
            ORDER BY entry_time DESC
            """
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_departed_vehicles(limit=300):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT license_plate,
                   COALESCE(vehicle_type, 'Xe'),
                   ticket_type,
                   entry_time,
                   exit_time,
                   COALESCE(fee, 0)
            FROM vehicle_logs
            WHERE status != 'Đang trong bãi'
              AND exit_time IS NOT NULL
            ORDER BY exit_time DESC
            LIMIT %s
            """,
            (limit,),
        )
        return cursor.fetchall()
    finally:
        conn.close()