from flask import Blueprint, render_template, redirect, url_for, flash
from app.utils.helpers import login_required, role_required
from app import mysql

reservasi_admin_bp = Blueprint('reservasi_admin_bp', __name__)

@reservasi_admin_bp.route('/admin/reservasi')
@login_required
@role_required('admin')
def reservasi_admin_list():
    """Show all reservations for admin"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            r.id_reservasi, 
            u.nama_pengguna, 
            r.total_harga, 
            r.status_pembayaran,
            DATE_FORMAT(r.tanggal_reservasi, '%%d %%M %%Y %%H:%%i') as tanggal_reservasi
        FROM reservasi r
        JOIN users u ON r.id_pengguna = u.id_pengguna
        ORDER BY r.tanggal_reservasi DESC
    """)
    reservasi = cur.fetchall()
    cur.close()

    return render_template('reservasi/admin_list.html', reservasi=reservasi)


@reservasi_admin_bp.route('/admin/reservasi/delete/<int:id>')
@login_required
@role_required('admin')
def reservasi_admin_delete(id):
    """Allow admin to delete a reservation (cleanup test or bad entry)"""
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM reservasi WHERE id_reservasi=%s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Reservasi berhasil dihapus.', 'success')
    return redirect(url_for('reservasi_admin_bp.reservasi_admin_list'))
