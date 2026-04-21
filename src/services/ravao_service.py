def car_in(plate, vehicle_type):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO vehicle_logs (license_plate, vehicle_type, time_in, status)
        VALUES (%s, %s, NOW(), 'IN')
    """, (plate, vehicle_type))

    conn.commit()
    conn.close()