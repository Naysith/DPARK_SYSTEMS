from app import mysql
from flask import flash, redirect, url_for
from app.utils.error_handler import handle_mysql_error

def add_pembayaran(id_reservasi, form):
    try:
        jumlah = int(form['jumlah_bayar'])
        metode = form['metode_pembayaran']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO pembayaran (id_reservasi, jumlah_bayar, metode_pembayaran)
            VALUES (%s, %s, %s)
        """, (id_reservasi, jumlah, metode))

        cur.execute("""
            UPDATE reservasi
            SET status_pembayaran = 'selesai'
            WHERE id_reservasi = %s
        """, (id_reservasi,))
        mysql.connection.commit()
        cur.close()

        flash('Pembayaran berhasil! Terima kasih telah memesan.', 'success')
        return redirect(url_for('reservasi_bp.reservasi_list'))

    except Exception as e:
        return handle_mysql_error(e, 'reservasi_bp.reservasi_list')
