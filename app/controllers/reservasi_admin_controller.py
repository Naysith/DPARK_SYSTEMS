
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.utils.helpers import login_required, role_required
from app import mysql
from app.utils.error_handler import handle_mysql_error

reservasi_admin_bp = Blueprint('reservasi_admin_bp', __name__)

@reservasi_admin_bp.route('/admin/reservasi')
@login_required
@role_required('admin')
def reservasi_admin_list():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                r.id_reservasi,
                u.nama_pengguna,
                r.total_harga,
                r.status_pembayaran,
                DATE_FORMAT(r.tanggal_reservasi, '%d %M %Y %H:%i') AS tanggal_reservasi,
                COUNT(t.id_tiket) AS jumlah_tiket
            FROM reservasi r
            JOIN pengguna u ON r.id_pengguna = u.id_pengguna
            LEFT JOIN tiket t ON r.id_reservasi = t.id_reservasi
            GROUP BY r.id_reservasi
            ORDER BY r.tanggal_reservasi DESC
        """)
        reservasi = cur.fetchall()
        cur.close()
    except Exception as e:
        return handle_mysql_error(e, 'reservasi_admin_bp.reservasi_admin_list')

    return render_template('reservasi/admin_list.html', reservasi=reservasi)

@reservasi_admin_bp.route('/admin/reservasi/delete/<int:id>')
@login_required
@role_required('admin')
def reservasi_admin_delete(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM reservasi WHERE id_reservasi=%s", (id,))
        mysql.connection.commit()
        cur.close()
        flash('Reservasi berhasil dihapus.', 'success')
    except Exception as e:
        return handle_mysql_error(e, 'reservasi_admin_bp.reservasi_admin_list')
    return redirect(url_for('reservasi_admin_bp.reservasi_admin_list'))

@reservasi_admin_bp.route('/admin/reservasi/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def reservasi_admin_add():
    from app.models import reservasi_model

    try:
        if request.method == 'POST':
            id_pengguna = request.form['id_pengguna']
            id_sesi = request.form['id_sesi']
            jumlah_tiket = request.form['jumlah_tiket']
            status_pembayaran = request.form.get('status_pembayaran', 'lunas')

            success = reservasi_model.add_reservasi(id_pengguna, id_sesi, jumlah_tiket, status_pembayaran)
            if success:
                return redirect(url_for('reservasi_admin_bp.reservasi_admin_list'))

        # Load available sessions and users for dropdown
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_sesi, nama_sesi FROM sesi")
        sesi_list = cur.fetchall()

        cur.execute("SELECT id_pengguna, nama_pengguna FROM pengguna WHERE peran='pelanggan'")
        user_list = cur.fetchall()

        cur.close()

        return render_template('reservasi/admin_add.html', sesi_list=sesi_list, user_list=user_list)
    except Exception as e:
        return handle_mysql_error(e, 'reservasi_admin_bp.reservasi_admin_list')
