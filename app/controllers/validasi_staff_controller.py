from flask import Blueprint, render_template
from app.utils.helpers import login_required, role_required
from app import mysql
from app.utils.error_handler import handle_mysql_error

validasi_staff_bp = Blueprint('validasi_staff_bp', __name__)

@validasi_staff_bp.route('/staff/validasi')
@login_required
@role_required('staff')
def staff_validasi_list():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT v.id_validasi, p.nama_pengguna, w.nama_wahana, v.waktu_validasi
            FROM validasi v
            JOIN pengguna p ON v.id_pengguna = p.id_pengguna
            JOIN wahana w ON v.id_wahana = w.id_wahana
            ORDER BY v.waktu_validasi DESC
        """)
        data = cur.fetchall()
        cur.close()
        return render_template('validasi/staff_list.html', validasi=data)
    except Exception as e:
        return handle_mysql_error(e, 'validasi_staff_bp.staff_validasi_list')
