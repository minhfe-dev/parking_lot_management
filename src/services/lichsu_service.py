import re

from data.connect_database import get_connection

# Thứ tự khóa khớp bảng Lịch sử trên UI (HistoryScreen)
HISTORY_ROW_KEYS = (
    "id_giao_dich",
    "license_plate",
    "ticket_type",
    "customer_name",
    "entry_time",
    "exit_time",
    "fee_or_status",
)


def _normalize_plate(plate: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", (plate or "").upper())


def _norm_plate_sql(expr: str) -> str:
    """Biểu thức SQL chuẩn hoá biển số (bỏ - . khoảng trắng, upper)."""
    return (
        f"UPPER(REPLACE(REPLACE(REPLACE({expr}, '-', ''), ' ', ''), '.', ''))"
    )


def _vehicle_logs_column_names(conn) -> set[str]:
    """Dùng cursor mặc định (tuple); SHOW COLUMNS không tương thích với dictionary=True."""
    cur = conn.cursor()
    try:
        cur.execute("SHOW COLUMNS FROM vehicle_logs")
        return {str(r[0]).lower() for r in cur.fetchall()}
    finally:
        cur.close()


def _pick_time_columns(cols: set[str]) -> tuple[str, str]:
    if "entry_time" in cols:
        t_in = "vl.entry_time"
    elif "time_in" in cols:
        t_in = "vl.time_in"
    else:
        raise RuntimeError("vehicle_logs: không tìm thấy cột entry_time hoặc time_in")

    if "exit_time" in cols:
        t_out = "vl.exit_time"
    elif "time_out" in cols:
        t_out = "vl.time_out"
    else:
        t_out = "NULL"

    return t_in, t_out


def _ticket_type_select(cols: set[str]) -> str:
    if "ticket_type" in cols:
        return "vl.ticket_type AS ticket_type"
    return "'Vé Ngày' AS ticket_type"


def _status_fee_select(cols: set[str]) -> str:
    """Cột cuối: đang trong bãi hoặc phí (VNĐ)."""
    if "fee" not in cols:
        fee_expr = "0"
    else:
        fee_expr = "vl.fee"

    if "status" not in cols:
        return f"CAST(COALESCE({fee_expr}, 0) AS CHAR) AS fee_or_status"

    return f"""
        CASE
            WHEN vl.status IN ('Đang trong bãi', 'IN') THEN 'Đang trong bãi'
            ELSE CAST(COALESCE({fee_expr}, 0) AS CHAR)
        END AS fee_or_status
    """.strip()


def _base_select_sql(cols: set[str]) -> tuple[str, str, str]:
    t_in, t_out = _pick_time_columns(cols)
    ticket_sql = _ticket_type_select(cols)
    status_sql = _status_fee_select(cols)

    customer_sql = f"""
        COALESCE(
            (
                SELECT mp.customer_name
                FROM monthly_passes mp
                WHERE {_norm_plate_sql('mp.license_plate')} = {_norm_plate_sql('vl.license_plate')}
                LIMIT 1
            ),
            ''
        ) AS customer_name
    """.strip()

    sql = f"""
        SELECT
            vl.id AS id_giao_dich,
            vl.license_plate AS license_plate,
            {ticket_sql},
            {customer_sql},
            {t_in} AS entry_time,
            {t_out} AS exit_time,
            {status_sql}
        FROM vehicle_logs vl
    """.strip()
    return sql, t_in, t_out


def _row_to_ordered_dict(row: dict) -> dict:
    lower = {str(k).lower(): v for k, v in row.items()}
    return {
        "id_giao_dich": lower.get("id_giao_dich"),
        "license_plate": lower.get("license_plate"),
        "ticket_type": lower.get("ticket_type"),
        "customer_name": lower.get("customer_name"),
        "entry_time": lower.get("entry_time"),
        "exit_time": lower.get("exit_time"),
        "fee_or_status": lower.get("fee_or_status"),
    }


def get_all():
    conn = get_connection()
    try:
        cols = _vehicle_logs_column_names(conn)
        cursor = conn.cursor(dictionary=True)
        base, t_in, _t_out = _base_select_sql(cols)
        query = f"{base} ORDER BY {t_in} DESC"
        cursor.execute(query)
        raw = cursor.fetchall() or []
        return [_row_to_ordered_dict(dict(r)) for r in raw]
    finally:
        conn.close()


def search(plate: str, name: str, t_from: str, t_to: str):
    conn = get_connection()
    try:
        cols = _vehicle_logs_column_names(conn)
        cursor = conn.cursor(dictionary=True)
        base, t_in, _t_out = _base_select_sql(cols)

        conds = [f"{t_in} >= %s", f"{t_in} <= %s"]
        params: list = [t_from, t_to]

        p = (plate or "").strip()
        if p:
            conds.append(f"{_norm_plate_sql('vl.license_plate')} LIKE %s")
            params.append(f"%{_normalize_plate(p)}%")

        n = (name or "").strip()
        if n:
            conds.append(
                f"""
                EXISTS (
                    SELECT 1 FROM monthly_passes mp2
                    WHERE {_norm_plate_sql('mp2.license_plate')} = {_norm_plate_sql('vl.license_plate')}
                      AND mp2.customer_name LIKE %s
                )
                """.strip()
            )
            params.append(f"%{n}%")

        where_sql = " AND ".join(conds)
        query = f"{base} WHERE {where_sql} ORDER BY {t_in} DESC"
        cursor.execute(query, tuple(params))
        raw = cursor.fetchall() or []
        return [_row_to_ordered_dict(dict(r)) for r in raw]
    finally:
        conn.close()
