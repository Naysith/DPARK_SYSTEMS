from flask import flash, redirect, url_for
from app import mysql
from app.utils.helpers import parse_datetime_local

# ---------------- GET SESSIONS ----------------
from datetime import datetime

def get_sesi_grouped():
    """
    Returns sessions grouped by wahana → month → day.
    """
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

        month_key = date.strftime("%Y-%m")   # e.g. 2025-10
        day_key = date.strftime("%Y-%m-%d")  # e.g. 2025-10-08

        grouped.setdefault(wahana_name, {})
        grouped[wahana_name].setdefault(month_key, {})
        grouped[wahana_name][month_key].setdefault(day_key, []).append(row)

    return grouped

# ---------------- ADD SESSION ----------------
def add_sesi(form):
    id_wahana = form['id_wahana']
    nama_sesi = form['nama_sesi']
    kuota = form['kuota']
    harga = form['harga']
    waktu_mulai = parse_datetime_local(form['waktu_mulai'])
    waktu_selesai = parse_datetime_local(form['waktu_selesai'])

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO sesi (id_wahana, nama_sesi, kuota, harga, waktu_mulai, waktu_selesai)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (id_wahana, nama_sesi, kuota, harga, waktu_mulai, waktu_selesai))
    mysql.connection.commit()
    cur.close()
    flash('Sesi berhasil ditambahkan!')
    return redirect(url_for('sesi_bp.sesi_list'))

# ---------------- EDIT SESSION ----------------
def edit_sesi(id, form):
    id_wahana = form['id_wahana']
    nama_sesi = form['nama_sesi']
    kuota = form['kuota']
    harga = form['harga']
    waktu_mulai = parse_datetime_local(form['waktu_mulai'])
    waktu_selesai = parse_datetime_local(form['waktu_selesai'])

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE sesi 
        SET id_wahana=%s, nama_sesi=%s, kuota=%s, harga=%s, waktu_mulai=%s, waktu_selesai=%s
        WHERE id_sesi=%s
    """, (id_wahana, nama_sesi, kuota, harga, waktu_mulai, waktu_selesai, id))
    mysql.connection.commit()
    cur.close()
    flash('Sesi berhasil diperbarui!')
    return redirect(url_for('sesi_bp.sesi_list'))

# ---------------- DELETE SESSION ----------------
def delete_sesi(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM sesi WHERE id_sesi=%s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Sesi dihapus!')
    return redirect(url_for('sesi_bp.sesi_list'))
