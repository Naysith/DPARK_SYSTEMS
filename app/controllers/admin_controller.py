from datetime import date, timedelta
from flask import Blueprint, render_template, session
from app.utils.helpers import login_required, role_required
from app.utils.sesi_auto import generate_auto_sesi
from app.utils.scheduler import get_scheduler_status
from app.utils.error_handler import handle_mysql_error
from app import mysql
from flask import jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash

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

@admin_bp.route('/admin/profile')
@login_required
@role_required('admin')
def profile_admin():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id_pengguna, nama_pengguna, email, nomor_telepon, alamat_rumah
            FROM pengguna
            WHERE id_pengguna = %s
        """, (session.get('id_pengguna'),))
        user = cur.fetchone()
        cur.close()
    except Exception as e:
        handle_mysql_error(e, 'admin_bp.profile_admin')
        user = None
    # reuse staff profile template so UI is identical
    return render_template('staff/profile_setting.html', user=user)

@admin_bp.route('/admin/profile/update_contact', methods=['POST'])
@login_required
@role_required('admin')
def update_profile_contact_admin():
    try:
        data = request.get_json() or {}
        nomor_telepon = (data.get('nomor_telepon') or '').strip()
        alamat_rumah = (data.get('alamat_rumah') or '').strip()
        id_pengguna = session.get('id_pengguna')
        if not id_pengguna:
            return jsonify(success=False, message='User tidak terautentikasi'), 401

        cur = mysql.connection.cursor()
        cur.execute("UPDATE pengguna SET nomor_telepon=%s, alamat_rumah=%s WHERE id_pengguna=%s",
                    (nomor_telepon, alamat_rumah, id_pengguna))
        mysql.connection.commit()
        cur.close()

        session['nomor_telepon'] = nomor_telepon
        session['alamat_rumah'] = alamat_rumah
        return jsonify(success=True, message='Informasi kontak berhasil disimpan',
                       nomor_telepon=nomor_telepon, alamat_rumah=alamat_rumah)
    except Exception as e:
        handle_mysql_error(e, 'admin_bp.update_profile_contact')
        return jsonify(success=False, message='Gagal menyimpan informasi kontak'), 500


@admin_bp.route('/admin/profile/update_account', methods=['POST'])
@login_required
@role_required('admin')
def update_profile_account_admin():
    try:
        data = request.get_json() or {}
        nama = (data.get('nama_pengguna') or '').strip()
        password = data.get('password')
        old_password = data.get('old_password')
        id_pengguna = session.get('id_pengguna')
        if not id_pengguna:
            return jsonify(success=False, message='User tidak terautentikasi'), 401

        cur = mysql.connection.cursor()
        cur.execute("SELECT password_hash FROM pengguna WHERE id_pengguna=%s", (id_pengguna,))
        row = cur.fetchone()
        current_hash = row[0] if row else None
        if isinstance(current_hash, (bytes, bytearray)):
            try:
                current_hash = current_hash.decode('utf-8')
            except:
                current_hash = str(current_hash)

        if password:
            if not old_password:
                cur.close()
                return jsonify(success=False, message='Password lama harus diisi'), 400
            if not current_hash or not check_password_hash(current_hash, old_password):
                cur.close()
                return jsonify(success=False, message='Password lama tidak cocok'), 403
            new_hash = generate_password_hash(password)
            cur.execute("UPDATE pengguna SET nama_pengguna=%s, password_hash=%s WHERE id_pengguna=%s",
                        (nama, new_hash, id_pengguna))
        else:
            cur.execute("UPDATE pengguna SET nama_pengguna=%s WHERE id_pengguna=%s", (nama, id_pengguna))

        mysql.connection.commit()
        cur.close()
        session['nama_pengguna'] = nama
        return jsonify(success=True, message='Informasi akun berhasil disimpan', nama_pengguna=nama)
    except Exception as e:
        handle_mysql_error(e, 'admin_bp.update_profile_account')
        return jsonify(success=False, message='Gagal menyimpan informasi akun'), 500

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
