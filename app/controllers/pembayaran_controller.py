from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from app.models.pembayaran_model import add_pembayaran
from app.utils.helpers import login_required, role_required
from app import mysql

pembayaran_bp = Blueprint('pembayaran_bp', __name__)

@pembayaran_bp.route('/pembayaran/<int:id_reservasi>', methods=['GET', 'POST'])
@login_required
@role_required('pelanggan')
def pembayaran_add(id_reservasi):
    # Fetch reservation info and cast ENUM to string in SQL
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id_reservasi, 
            total_harga, 
            CAST(status_pembayaran AS CHAR) AS status_pembayaran
        FROM reservasi
        WHERE id_reservasi = %s AND id_pengguna = %s
    """, (id_reservasi, session['id_pengguna']))
    row = cur.fetchone()
    cur.close()

    if not row:
        flash('Reservasi tidak ditemukan!', 'danger')
        return redirect('/reservasi')

    # Explicitly assign variables
    id_reservasi_db = int(row[0])
    total_harga_db = int(row[1])
    status_pembayaran_db = row[2]  # will always be 'menunggu' or 'selesai'

    # Check if reservation is already paid
    if status_pembayaran_db == 'selesai':
        flash('Reservasi ini sudah dibayar.', 'info')
        return redirect(url_for('reservasi_bp.reservasi_list'))

    if request.method == 'POST':
        # Lock the payment to total_harga
        form = {
            'jumlah_bayar': total_harga_db,  # guaranteed correct
            'metode_pembayaran': request.form['metode_pembayaran']
        }
        # Call the model function
        add_pembayaran(id_reservasi_db, form)
        flash('Pembayaran berhasil!', 'success')
        return redirect(url_for('reservasi_bp.reservasi_list'))

    # Pass data to template
    reservasi = {
        'id_reservasi': id_reservasi_db,
        'total_harga': total_harga_db,
        'status_pembayaran': status_pembayaran_db
    }
    return render_template('pembayaran/form.html', reservasi=reservasi)
