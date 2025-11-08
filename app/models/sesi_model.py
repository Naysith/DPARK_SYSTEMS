from flask import flash, redirect, url_for
from app import mysql
from app.utils.helpers import parse_datetime_local
from app.utils.error_handler import handle_mysql_error
from datetime import datetime

def get_sesi(id=None, available_only=False):
    cur = mysql.connection.cursor()
    if id:
        cur.execute("""
            SELECT s.id_sesi, s.id_wahana, s.nama_sesi, s.kuota, s.harga, s.waktu_mulai, s.waktu_selesai
            FROM sesi s
            JOIN wahana w ON s.id_wahana = w.id_wahana
            WHERE s.id_sesi=%s
        """, (id,))
        data = cur.fetchone()
    elif available_only:
        cur.execute("""
            SELECT s.id_sesi, s.nama_sesi, s.kuota, s.harga, w.nama_wahana
            FROM sesi s
            JOIN wahana w ON s.id_wahana = w.id_wahana
            WHERE s.kuota > 0
            ORDER BY w.nama_wahana, s.waktu_mulai
        """)
        data = cur.fetchall()
    else:
        cur.execute("""
            SELECT s.id_sesi, s.nama_sesi, s.kuota, s.harga, w.nama_wahana
            FROM sesi s
            JOIN wahana w ON s.id_wahana = w.id_wahana
            ORDER BY w.nama_wahana, s.waktu_mulai
        """)
        data = cur.fetchall()
    cur.close()
    return data

def get_sesi_grouped():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT s.id_sesi, s.nama_sesi, s.kuota, s.harga,
               s.waktu_mulai, s.waktu_selesai, w.nama_wahana
        FROM sesi s
        JOIN wahana w ON s.id_wahana = w.id_wahana
        ORDER BY w.nama_wahana, s.waktu_mulai
    """)
    rows = cur.fetchall()
    cur.close()

    grouped = {}
    for row in rows:
        wahana_name = row[6]
        date = row[4].date() if row[4] else None
        if not date:
            continue
        month_key = date.strftime("%Y-%m")
        day_key = date.strftime("%Y-%m-%d")
        grouped.setdefault(wahana_name, {})
        grouped[wahana_name].setdefault(month_key, {})
        grouped[wahana_name][month_key].setdefault(day_key, []).append(row)
    return grouped

def get_sesi_by_wahana(id_wahana):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT s.id_sesi, s.nama_sesi, s.kuota, s.harga, s.waktu_mulai, s.waktu_selesai
        FROM sesi s
        WHERE s.id_wahana = %s
        ORDER BY s.id_sesi ASC
    """, (id_wahana,))
    rows = cur.fetchall()
    cur.close()
    result = []
    for row in rows:
        result.append({
            'id_sesi': row[0],
            'nama_sesi': row[1],
            'kuota': row[2],
            'harga': row[3],
            'waktu_mulai': row[4],
            'waktu_selesai': row[5]
        })
    return result

def get_sesi_paginated(page=1, per_page=10, wahana_filter=None, month_filter=None):
    from app import mysql
    cur = mysql.connection.cursor()

    offset = (page - 1) * per_page

    base_query = """
        SELECT s.id_sesi, s.nama_sesi, s.kuota, s.harga, s.waktu_mulai, s.waktu_selesai, w.nama_wahana
        FROM sesi s
        JOIN wahana w ON s.id_wahana = w.id_wahana
    """
    conditions = []
    params = []

    if wahana_filter:
        conditions.append("w.nama_wahana = %s")
        params.append(wahana_filter)
    if month_filter:
        conditions.append("DATE_FORMAT(s.waktu_mulai, '%%Y-%%m') = %s")
        params.append(month_filter)

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    base_query += " ORDER BY w.nama_wahana, s.waktu_mulai LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    cur.execute(base_query, params)
    rows = cur.fetchall()

    # Count total for pagination
    count_query = """
        SELECT COUNT(*) FROM sesi s
        JOIN wahana w ON s.id_wahana = w.id_wahana
    """
    if conditions:
        count_query += " WHERE " + " AND ".join(conditions)
    cur.execute(count_query, params[:-2])
    total = cur.fetchone()[0]

    cur.close()
    return rows, total



def add_sesi(form):
    try:
        cur = mysql.connection.cursor()

        # --- Validate required fields ---
        id_wahana = form.get('id_wahana')
        nama_sesi = (form.get('nama_sesi') or '').strip()
        kuota = form.get('kuota')
        harga = form.get('harga')
        waktu_mulai_raw = form.get('waktu_mulai')
        waktu_selesai_raw = form.get('waktu_selesai')

        if not id_wahana or not nama_sesi or not kuota or not harga or not waktu_mulai_raw or not waktu_selesai_raw:
            flash('\u274c Semua field wajib diisi!', 'danger')
            cur.close()
            return redirect(url_for('sesi_bp.sesi_add', id_wahana=id_wahana))

        # --- Validate numeric fields ---
        try:
            id_wahana_int = int(id_wahana)
            kuota_int = int(kuota)
            harga_int = int(harga)
        except ValueError:
            flash('\u274c Kuota, harga, dan ID wahana harus berupa angka.', 'danger')
            cur.close()
            return redirect(url_for('sesi_bp.sesi_add', id_wahana=id_wahana))

        if kuota_int <= 0:
            flash('\u274c Kuota harus lebih besar dari 0.', 'danger')
            cur.close()
            return redirect(url_for('sesi_bp.sesi_add', id_wahana=id_wahana))

        if harga_int < 0:
            flash('\u274c Harga tidak boleh negatif.', 'danger')
            cur.close()
            return redirect(url_for('sesi_bp.sesi_add', id_wahana=id_wahana))

        # --- Validate wahana exists ---
        cur.execute("SELECT id_wahana FROM wahana WHERE id_wahana=%s", (id_wahana_int,))
        if not cur.fetchone():
            flash('\u274c Wahana tidak ditemukan.', 'danger')
            cur.close()
            return redirect(url_for('sesi_bp.sesi_add', id_wahana=id_wahana))

        # --- Validate datetime fields and ordering ---
        try:
            mulai_dt = datetime.strptime(waktu_mulai_raw, '%Y-%m-%dT%H:%M')
            selesai_dt = datetime.strptime(waktu_selesai_raw, '%Y-%m-%dT%H:%M')
        except Exception:
            flash('\u274c Format tanggal/waktu tidak valid.', 'danger')
            cur.close()
            return redirect(url_for('sesi_bp.sesi_add', id_wahana=id_wahana))

        if mulai_dt >= selesai_dt:
            flash('\u274c Waktu mulai harus sebelum waktu selesai.', 'danger')
            cur.close()
            return redirect(url_for('sesi_bp.sesi_add', id_wahana=id_wahana))

        waktu_mulai = parse_datetime_local(waktu_mulai_raw)
        waktu_selesai = parse_datetime_local(waktu_selesai_raw)

        # --- Prevent duplicate session (same wahana, same start) ---
        cur.execute("SELECT id_sesi FROM sesi WHERE id_wahana=%s AND waktu_mulai=%s",
                    (id_wahana_int, waktu_mulai))
        if cur.fetchone():
            flash('\u274c Sesi sudah ada pada waktu tersebut untuk wahana ini.', 'danger')
            cur.close()
            return redirect(url_for('sesi_bp.sesi_add', id_wahana=id_wahana))

        # --- Insert new session ---
        cur.execute("""
            INSERT INTO sesi (id_wahana, nama_sesi, kuota, harga, waktu_mulai, waktu_selesai)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            id_wahana_int, nama_sesi, kuota_int, harga_int,
            waktu_mulai, waktu_selesai
        ))
        mysql.connection.commit()
        cur.close()
        flash('Sesi berhasil ditambahkan!', 'success')
        return redirect(url_for('sesi_bp.sesi_list_by_wahana', id_wahana=id_wahana))
    except Exception as e:
        return handle_mysql_error(e, 'sesi_bp.sesi_list_by_wahana')

def edit_sesi(id, form):
    try:
        cur = mysql.connection.cursor()

        # --- Validate required fields ---
        id_wahana = form.get('id_wahana')
        nama_sesi = (form.get('nama_sesi') or '').strip()
        kuota = form.get('kuota')
        harga = form.get('harga')
        waktu_mulai_raw = form.get('waktu_mulai')
        waktu_selesai_raw = form.get('waktu_selesai')

        if not id_wahana or not nama_sesi or not kuota or not harga or not waktu_mulai_raw or not waktu_selesai_raw:
            flash('\u274c Semua field wajib diisi!', 'danger')
            cur.close()
            return redirect(url_for('sesi_bp.sesi_edit', id=id))

        # --- Validate numeric fields ---
        try:
            id_wahana_int = int(id_wahana)
            kuota_int = int(kuota)
            harga_int = int(harga)
        except ValueError:
            flash('\u274c Kuota, harga, dan ID wahana harus berupa angka.', 'danger')
            cur.close()
            return redirect(url_for('sesi_bp.sesi_edit', id=id))

        if kuota_int <= 0:
            flash('\u274c Kuota harus lebih besar dari 0.', 'danger')
            cur.close()
            return redirect(url_for('sesi_bp.sesi_edit', id=id))

        if harga_int < 0:
            flash('\u274c Harga tidak boleh negatif.', 'danger')
            cur.close()
            return redirect(url_for('sesi_bp.sesi_edit', id=id))

        # --- Validate wahana exists ---
        cur.execute("SELECT id_wahana FROM wahana WHERE id_wahana=%s", (id_wahana_int,))
        if not cur.fetchone():
            flash('\u274c Wahana tidak ditemukan.', 'danger')
            cur.close()
            return redirect(url_for('sesi_bp.sesi_edit', id=id))

        # --- Validate datetime fields and ordering ---
        try:
            mulai_dt = datetime.strptime(waktu_mulai_raw, '%Y-%m-%dT%H:%M')
            selesai_dt = datetime.strptime(waktu_selesai_raw, '%Y-%m-%dT%H:%M')
        except Exception:
            flash('\u274c Format tanggal/waktu tidak valid.', 'danger')
            cur.close()
            return redirect(url_for('sesi_bp.sesi_edit', id=id))

        if mulai_dt >= selesai_dt:
            flash('\u274c Waktu mulai harus sebelum waktu selesai.', 'danger')
            cur.close()
            return redirect(url_for('sesi_bp.sesi_edit', id=id))

        waktu_mulai = parse_datetime_local(waktu_mulai_raw)
        waktu_selesai = parse_datetime_local(waktu_selesai_raw)

        cur.execute("""
            UPDATE sesi 
            SET id_wahana=%s, nama_sesi=%s, kuota=%s, harga=%s, waktu_mulai=%s, waktu_selesai=%s
            WHERE id_sesi=%s
        """, (
            id_wahana_int, nama_sesi, kuota_int, harga_int, waktu_mulai, waktu_selesai,
            id
        ))
        mysql.connection.commit()
        cur.close()
        flash('Sesi berhasil diperbarui!', 'success')
        return redirect(url_for('sesi_bp.sesi_list_by_wahana', id_wahana=id_wahana))
    except Exception as e:
        return handle_mysql_error(e, ('sesi_bp.sesi_edit', {'id': id}))

def delete_sesi(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_wahana FROM sesi WHERE id_sesi=%s", (id,))
        result = cur.fetchone()
        id_wahana = result[0] if result else None

        cur.execute("DELETE FROM sesi WHERE id_sesi=%s", (id,))
        mysql.connection.commit()
        cur.close()
        flash('Sesi dihapus!', 'info')
        if id_wahana:
            return redirect(url_for('sesi_bp.sesi_list_by_wahana', id_wahana=id_wahana))
        else:
            return redirect(url_for('wahana_bp.wahana_list'))
    except Exception as e:
        return handle_mysql_error(e, 'sesi_bp.sesi_list_by_wahana')
    

def find_sesi_for_date_and_period(id_wahana, date_str, period):
    """Find a single sesi row for wahana on a specific date and period.
    period: 'pagi' (morning), 'siang' (afternoon), 'malam' (evening)
    Returns the first matching row or None.
    """
    cur = mysql.connection.cursor()
    # naive period mapping to time ranges
    if period == 'pagi':
        time_cond = "TIME(w.waktu_mulai) BETWEEN '06:00:00' AND '11:59:59'"
    elif period == 'siang':
        time_cond = "TIME(w.waktu_mulai) BETWEEN '12:00:00' AND '16:59:59'"
    else:
        time_cond = "TIME(w.waktu_mulai) BETWEEN '17:00:00' AND '23:59:59'"

    query = f"""
        SELECT s.id_sesi, s.nama_sesi, s.kuota, s.harga, s.waktu_mulai, s.waktu_selesai, w.nama_wahana
        FROM sesi s
        JOIN wahana w ON s.id_wahana = w.id_wahana
        WHERE s.id_wahana = %s AND DATE(s.waktu_mulai) = %s AND s.kuota > 0 AND {time_cond}
        ORDER BY s.waktu_mulai LIMIT 1
    """
    cur.execute(query, (id_wahana, date_str))
    row = cur.fetchone()
    cur.close()
    return row
