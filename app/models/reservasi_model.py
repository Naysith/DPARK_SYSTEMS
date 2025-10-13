from app import mysql
from datetime import datetime
from uuid import uuid4
from flask import flash, redirect, url_for
from app.utils.error_handler import handle_mysql_error

def get_reservasi(user):
    cur = mysql.connection.cursor()
    if user['peran'] == 'admin':
        cur.execute("""
            SELECT r.id_reservasi, u.nama_pengguna, r.total_harga, 
                   r.status_pembayaran, r.tanggal_reservasi
            FROM reservasi r
            JOIN users u ON r.id_pengguna = u.id_pengguna
            ORDER BY r.tanggal_reservasi DESC
        """)
    else:
        cur.execute("""
            SELECT id_reservasi, total_harga, status_pembayaran, tanggal_reservasi
            FROM reservasi
            WHERE id_pengguna = %s
            ORDER BY tanggal_reservasi DESC
        """, (user['id_pengguna'],))
    data = cur.fetchall()
    cur.close()
    return data

def add_reservasi(form, user):
    try:
        id_pengguna = user['id_pengguna']
        id_sesi = form['id_sesi']
        jumlah = int(form['jumlah'])

        cur = mysql.connection.cursor()
        # Get session info
        cur.execute("SELECT harga, kuota FROM sesi WHERE id_sesi = %s", (id_sesi,))
        sesi = cur.fetchone()

        if not sesi:
            flash('Sesi tidak ditemukan!', 'danger')
            return redirect(url_for('reservasi_bp.reservasi_add'))

        harga, kuota = sesi
        if jumlah > kuota:
            flash('Kuota tidak cukup!', 'warning')
            return redirect(url_for('reservasi_bp.reservasi_add'))

        total = harga * jumlah
        kode_unik = "R-" + uuid4().hex[:8]

        cur.execute("""
            INSERT INTO reservasi (id_pengguna, total_harga, status_pembayaran, kode_unik, tanggal_reservasi)
            VALUES (%s, %s, 'menunggu', %s, %s)
        """, (id_pengguna, total, kode_unik, datetime.now()))
        reservasi_id = cur.lastrowid

        # Generate tickets
        for _ in range(jumlah):
            kode_tiket = "T-" + uuid4().hex[:10]
            cur.execute("""
                INSERT INTO tiket (id_reservasi, id_sesi, kode_tiket)
                VALUES (%s, %s, %s)
            """, (reservasi_id, id_sesi, kode_tiket))

        # Update session quota
        cur.execute("UPDATE sesi SET kuota = kuota - %s WHERE id_sesi = %s", (jumlah, id_sesi))
        mysql.connection.commit()
        cur.close()

        flash('Reservasi berhasil dibuat!', 'success')
        return redirect(url_for('reservasi_bp.reservasi_list'))

    except Exception as e:
        return handle_mysql_error(e, 'reservasi_bp.reservasi_add')
