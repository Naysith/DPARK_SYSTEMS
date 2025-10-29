from flask import Blueprint, render_template
from app.utils.helpers import login_required, role_required
from app.utils.sesi_auto import generate_auto_sesi
from app.utils.scheduler import get_scheduler_status
from app.utils.error_handler import handle_mysql_error
from app import mysql

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    try:
        cur = mysql.connection.cursor()

        # Total validasi (all time)
        cur.execute("SELECT COUNT(*) FROM validasi")
        total_validasi = cur.fetchone()[0]

        # Tiket yang sudah dibayar hari ini
        cur.execute("""
            SELECT COUNT(*) 
            FROM reservasi 
            WHERE DATE(tanggal_reservasi) = CURDATE()
            AND status_pembayaran = 'selesai'
        """)
        tiket_hari_ini = cur.fetchone()[0]

        # Validasi hari ini
        cur.execute("""
            SELECT COUNT(*) 
            FROM validasi 
            WHERE DATE(waktu_validasi) = CURDATE()
        """)
        validasi_hari_ini = cur.fetchone()[0]

        # Log validasi (latest 10)
        cur.execute("""
            SELECT 
                v.id_validasi,
                p.nama_pengguna,
                w.nama_wahana,
                v.waktu_validasi
            FROM validasi v
            JOIN pengguna p ON v.id_pengguna = p.id_pengguna
            JOIN wahana w ON v.id_wahana = w.id_wahana
            ORDER BY v.waktu_validasi DESC
            LIMIT 10
        """)
        validasi = cur.fetchall()
        cur.close()

    except Exception as e:
        return handle_mysql_error(e, 'admin_bp.admin_dashboard')

    return render_template(
        'admin/admin_dashboard.html',
        total_validasi=total_validasi,
        tiket_hari_ini=tiket_hari_ini,
        validasi_hari_ini=validasi_hari_ini,
        validasi=validasi
    )
    
@admin_bp.route('/admin/generate_sesi', endpoint='generate_sesi_auto')
@role_required('admin')
def generate_sesi_auto_route():
    try:
        generate_auto_sesi()
    except Exception as e:
        return handle_mysql_error(e, 'admin_bp.admin_dashboard')
    return "✅ Auto session generation complete! Check your sesi list."

@admin_bp.route('/admin/scheduler_status')
@role_required('admin')
def scheduler_status():
    try:
        status = get_scheduler_status()
    except Exception as e:
        return handle_mysql_error(e, 'admin_bp.admin_dashboard')
    return render_template('scheduler_status.html', status=status)

@admin_bp.route('/admin/validasi')
@login_required
@role_required('admin')
def validasi_admin():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                v.id_validasi,
                p.nama_pengguna,
                w.nama_wahana,
                v.waktu_validasi
            FROM validasi v
            JOIN pengguna p ON v.id_pengguna = p.id_pengguna
            JOIN wahana w ON v.id_wahana = w.id_wahana
            ORDER BY v.waktu_validasi DESC
        """)
        validasi = cur.fetchall()
        cur.close()
    except Exception as e:
        return handle_mysql_error(e, 'admin_bp.validasi_admin')

    return render_template('admin/validasi_admin.html', validasi=validasi)
