from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from app.models.pembayaran_model import add_pembayaran
from app.utils.helpers import login_required, role_required
from app import mysql

pembayaran_bp = Blueprint('pembayaran_bp', __name__)

@pembayaran_bp.route('/pembayaran/<int:id_reservasi>', methods=['GET', 'POST'])
@login_required
@role_required('pelanggan')
def pembayaran_add(id_reservasi):
    # Fetch reservation info
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id_reservasi, total_harga, status_pembayaran
        FROM reservasi
        WHERE id_reservasi = %s AND id_pengguna = %s
    """, (id_reservasi, session['id_pengguna']))
    reservasi = cur.fetchone()
    cur.close()

    if not reservasi:
        flash('Reservasi tidak ditemukan!', 'danger')
        return redirect('/reservasi')

    if reservasi[2] == 'selesai':
        flash('Reservasi ini sudah dibayar.', 'info')
        return redirect(url_for('reservasi_bp.reservasi_list'))

    if request.method == 'POST':
        # Lock the payment to total_harga
        form = {
            'jumlah_bayar': reservasi[1],
            'metode_pembayaran': request.form['metode_pembayaran']
        }
        return add_pembayaran(id_reservasi, form)

    return render_template('pembayaran/form.html', reservasi=reservasi)
