from datetime import datetime, timedelta, time

DEFAULT_SESSION_PRICE = 50000

def generate_auto_sesi():
    from app import mysql
    cur = mysql.connection.cursor()

    # Fetch all wahana
    cur.execute("SELECT id_wahana, nama_wahana FROM wahana")
    wahana_list = cur.fetchall()

    today = datetime.now().date()
    end_date = today + timedelta(days=7)

    sessions_per_day = [
        ("Pagi", time(9, 0),  time(13, 0)),
        ("Siang", time(13, 0), time(17, 0)),
        ("Malam", time(17, 0), time(21, 0)),
    ]

    added_count = 0
    for w in wahana_list:
        id_wahana, nama_wahana = w
        date = today
        while date <= end_date:
            for sesi_name, start, end in sessions_per_day:
                start_dt = datetime.combine(date, start)
                end_dt = datetime.combine(date, end)

                # Skip if already exists
                cur.execute("""
                    SELECT id_sesi FROM sesi
                    WHERE id_wahana=%s AND waktu_mulai=%s
                """, (id_wahana, start_dt))
                if cur.fetchone():
                    continue

                cur.execute("""
                    INSERT INTO sesi (id_wahana, nama_sesi, kuota, harga, waktu_mulai, waktu_selesai)
                    VALUES (%s,%s,%s,%s,%s,%s)
                """, (id_wahana, sesi_name, 50, DEFAULT_SESSION_PRICE, start_dt, end_dt))
                added_count += 1
            date += timedelta(days=1)

    mysql.connection.commit()
    cur.close()
    print(f"✅ Generated {added_count} sessions with default price Rp {DEFAULT_SESSION_PRICE:,}.")