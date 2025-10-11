from datetime import datetime, timedelta, time

def generate_auto_sesi():
    from app import mysql
    """
    - 3 sessions per day (09–13, 13–17, 17–21)
    - Each with kuota = 50
    - Add-only mode (never updates existing ones)
    """
    cur = mysql.connection.cursor()

    # 1️⃣ Fetch all rides (wahana)
    cur.execute("SELECT id_wahana, nama_wahana FROM wahana")
    wahana_list = cur.fetchall()

    if not wahana_list:
        print("⚠️ No wahana found — cannot generate sessions.")
        cur.close()
        return

    today = datetime.now().date()
    end_date = today + timedelta(days=90)  # ~3 months ahead

    # Define standard daily session windows
    sessions_per_day = [
        ("Sesi Pagi", time(9, 0), time(13, 0)),
        ("Sesi Siang", time(13, 0), time(17, 0)),
        ("Sesi Malam", time(17, 0), time(21, 0)),
    ]

    added_count = 0

    for wahana_id, wahana_nama in wahana_list:
        # 2️⃣ Find the last session date for this wahana
        cur.execute("SELECT MAX(waktu_mulai) FROM sesi WHERE id_wahana=%s", (wahana_id,))
        last_date_row = cur.fetchone()
        last_date = last_date_row[0].date() if last_date_row[0] else today - timedelta(days=1)

        # Start from the next day after last_date
        current_date = max(today, last_date + timedelta(days=1))

        while current_date <= end_date:
            for nama_sesi, start_time, end_time in sessions_per_day:
                waktu_mulai = datetime.combine(current_date, start_time)
                waktu_selesai = datetime.combine(current_date, end_time)

                # 3️⃣ Check if session already exists (avoid duplicates)
                cur.execute("""
                    SELECT COUNT(*) FROM sesi
                    WHERE id_wahana=%s AND waktu_mulai=%s AND waktu_selesai=%s
                """, (wahana_id, waktu_mulai, waktu_selesai))
                exists = cur.fetchone()[0]

                if exists:
                    continue  # skip existing sessions safely

                # 4️⃣ Insert new session
                cur.execute("""
                    INSERT INTO sesi (id_wahana, nama_sesi, kuota, harga, waktu_mulai, waktu_selesai)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (wahana_id, nama_sesi, 50, 0, waktu_mulai, waktu_selesai))
                added_count += 1

            current_date += timedelta(days=1)

    mysql.connection.commit()
    cur.close()
    print(f"✅ Generated {added_count} new sessions up to {end_date.strftime('%Y-%m-%d')} for {len(wahana_list)} wahana.")
