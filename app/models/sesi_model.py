from flask import flash, redirect, url_for
from app import mysql
from app.utils.helpers import parse_datetime_local
from app.utils.error_handler import handle_mysql_error

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

def add_sesi(form):
    try:
        cur = mysql.connection.cursor()
        waktu_mulai = parse_datetime_local(form['waktu_mulai'])
        if cur.execute("SELECT id_sesi FROM sesi WHERE id_wahana=%s AND waktu_mulai=%s",
                       (form['id_wahana'], waktu_mulai)):
            flash("❌ Sesi sudah ada!", "danger")
            return redirect(url_for('sesi_bp.sesi_add'))

        cur.execute("""
            INSERT INTO sesi (id_wahana, nama_sesi, kuota, harga, waktu_mulai, waktu_selesai)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            form['id_wahana'], form['nama_sesi'], form['kuota'], form['harga'],
            waktu_mulai, parse_datetime_local(form['waktu_selesai'])
        ))
        mysql.connection.commit()
        cur.close()
        flash('Sesi berhasil ditambahkan!', 'success')
        return redirect(url_for('sesi_bp.sesi_list'))
    except Exception as e:
        return handle_mysql_error(e, 'sesi_bp.sesi_add')

def edit_sesi(id, form):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE sesi 
            SET id_wahana=%s, nama_sesi=%s, kuota=%s, harga=%s, waktu_mulai=%s, waktu_selesai=%s
            WHERE id_sesi=%s
        """, (
            form['id_wahana'], form['nama_sesi'], form['kuota'], form['harga'],
            parse_datetime_local(form['waktu_mulai']), parse_datetime_local(form['waktu_selesai']),
            id
        ))
        mysql.connection.commit()
        cur.close()
        flash('Sesi berhasil diperbarui!', 'success')
        return redirect(url_for('sesi_bp.sesi_list'))
    except Exception as e:
        return handle_mysql_error(e, 'sesi_bp.sesi_edit')

def delete_sesi(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM sesi WHERE id_sesi=%s", (id,))
        mysql.connection.commit()
        cur.close()
        flash('Sesi dihapus!', 'info')
        return redirect(url_for('sesi_bp.sesi_list'))
    except Exception as e:
        return handle_mysql_error(e, 'sesi_bp.sesi_list')
