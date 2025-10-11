from flask import flash, redirect, url_for
from app import mysql
from app.utils.helpers import parse_datetime_local

# ---------------- GET SESSIONS ----------------
def get_sesi(id=None):
    cur = mysql.connection.cursor()
    if id:
        cur.execute("""
            SELECT s.id_sesi, w.nama_wahana, s.nama_sesi, s.kuota, s.harga, s.waktu_mulai, s.waktu_selesai
            FROM sesi s 
            JOIN wahana w ON s.id_wahana = w.id_wahana
            WHERE s.id_sesi = %s
        """, (id,))
        data = cur.fetchone()
    else:
        cur.execute("""
            SELECT s.id_sesi, w.nama_wahana, s.nama_sesi, s.kuota, s.harga, s.waktu_mulai, s.waktu_selesai
            FROM sesi s 
            JOIN wahana w ON s.id_wahana = w.id_wahana
            ORDER BY s.waktu_mulai DESC
        """)
        data = cur.fetchall()
    cur.close()
    return data

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
