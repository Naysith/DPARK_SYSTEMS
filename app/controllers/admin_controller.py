from datetime import date, timedelta
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

        cur.execute("SELECT COUNT(*) FROM validasi")
        total_validasi = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) 
            FROM reservasi 
            WHERE DATE(tanggal_reservasi) = CURDATE()
            AND status_pembayaran = 'selesai'
        """)
        tiket_hari_ini = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) 
            FROM validasi 
            WHERE DATE(waktu_validasi) = CURDATE()
        """)
        validasi_hari_ini = cur.fetchone()[0]

        cur.execute("SELECT COALESCE(SUM(jumlah_bayar), 0) FROM pembayaran WHERE DATE(tanggal_bayar) = CURDATE()")
        pendapatan_hari_ini = cur.fetchone()[0] or 0

        cur.execute("""
            SELECT COALESCE(SUM(jumlah_bayar), 0)
            FROM pembayaran
            WHERE YEARWEEK(DATE(tanggal_bayar), 1) = YEARWEEK(CURDATE(), 1)
        """)
        pendapatan_minggu_ini = cur.fetchone()[0] or 0

        cur.execute("""
            SELECT COALESCE(SUM(jumlah_bayar), 0)
            FROM pembayaran
            WHERE MONTH(tanggal_bayar) = MONTH(CURDATE()) AND YEAR(tanggal_bayar) = YEAR(CURDATE())
        """)
        pendapatan_bulan_ini = cur.fetchone()[0] or 0

        # Statistik 7 hari terakhir
        today = date.today()
        start_date = today - timedelta(days=6)
        cur.execute("""
            SELECT DATE(tanggal_reservasi) AS d, COUNT(*) AS cnt
            FROM reservasi
            WHERE DATE(tanggal_reservasi) BETWEEN %s AND %s
              AND status_pembayaran = 'selesai'
            GROUP BY DATE(tanggal_reservasi)
            ORDER BY DATE(tanggal_reservasi)
        """, (start_date, today))
        rows = cur.fetchall()
        counts_map = {r[0]: r[1] for r in rows}

        weekly_labels = []
        weekly_counts = []
        for i in range(7):
            d = start_date + timedelta(days=i)
            weekly_labels.append(d.strftime('%a'))
            weekly_counts.append(counts_map.get(d, 0))

        chart_max = max(weekly_counts) if weekly_counts else 0
        if chart_max == 0:
            chart_max = 5
        chart_ticks = [chart_max, int(chart_max * 0.75), int(chart_max * 0.5), int(chart_max * 0.25), 0]

        # Ambil riwayat validasi terakhir
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
        validasi=validasi,
        pendapatan_hari_ini=pendapatan_hari_ini,
        pendapatan_minggu_ini=pendapatan_minggu_ini,
        pendapatan_bulan_ini=pendapatan_bulan_ini,
        weekly_labels=weekly_labels,
        weekly_counts=weekly_counts,
        chart_max=chart_max,
        chart_ticks=chart_ticks
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
