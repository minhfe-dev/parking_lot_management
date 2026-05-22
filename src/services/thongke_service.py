from datetime import datetime, timedelta

from data.connect_database import get_connection
from src.services.ravao_service import backfill_vehicle_types_in_lot, vehicle_type_expr_sql


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
    backfill_vehicle_types_in_lot()
    vt_sql = vehicle_type_expr_sql("vl")
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"""
            SELECT vl.license_plate,
                   {vt_sql},
                   vl.ticket_type,
                   vl.entry_time
            FROM vehicle_logs vl
            WHERE vl.status = 'Đang trong bãi'
            ORDER BY vl.entry_time DESC
            """
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_departed_vehicles(limit=300):
    vt_sql = vehicle_type_expr_sql("vl")
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"""
            SELECT vl.license_plate,
                   {vt_sql},
                   vl.ticket_type,
                   vl.entry_time,
                   vl.exit_time,
                   COALESCE(vl.fee, 0)
            FROM vehicle_logs vl
            WHERE vl.status != 'Đang trong bãi'
              AND vl.exit_time IS NOT NULL
            ORDER BY vl.exit_time DESC
            LIMIT %s
            """,
            (limit,),
        )
        return cursor.fetchall()
    finally:
        conn.close()