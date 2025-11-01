from flask import Blueprint, render_template, request, session, redirect, url_for, flash
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
        flash('✅ Sesi otomatis berhasil digenerate untuk semua wahana selama 90 hari ke depan!', 'success')
    except Exception as e:
        return handle_mysql_error(e, 'admin_bp.generate_sesi_auto')
    return redirect(url_for('wahana_bp.wahana_list'))

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

@admin_bp.route('/admin/profile', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_profile():
    try:
        cur = mysql.connection.cursor()

        if request.method == 'POST':
            nama = request.form.get('nama_pengguna')
            email = request.form.get('email')
            nomor = request.form.get('nomor_telepon')
            alamat = request.form.get('alamat_rumah')
            password = request.form.get('password')

            # Update only non-empty fields
            if password:
                cur.execute("""
                    UPDATE pengguna
                    SET nama_pengguna=%s, email=%s, nomor_telepon=%s, alamat_rumah=%s, password_hash=SHA2(%s, 256)
                    WHERE id_pengguna=%s
                """, (nama, email, nomor, alamat, password, session['id_pengguna']))
            else:
                cur.execute("""
                    UPDATE pengguna
                    SET nama_pengguna=%s, email=%s, nomor_telepon=%s, alamat_rumah=%s
                    WHERE id_pengguna=%s
                """, (nama, email, nomor, alamat, session['id_pengguna']))
            
            mysql.connection.commit()
            flash('✅ Profil berhasil diperbarui!', 'success')
            return redirect(url_for('admin_bp.admin_profile'))

        # --- GET profile ---
        cur.execute("""
            SELECT nama_pengguna, email, nomor_telepon, alamat_rumah
            FROM pengguna
            WHERE id_pengguna = %s
        """, (session['id_pengguna'],))
        profile = cur.fetchone()
        cur.close()

    except Exception as e:
        return handle_mysql_error(e, 'admin_bp.admin_profile')

    return render_template('admin/profile.html', profile=profile)

@admin_bp.route('/admin/staff')
@login_required
@role_required('admin')
def admin_staff_list():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id_pengguna, nama_pengguna, email, nomor_telepon
            FROM pengguna
            WHERE peran = 'staff'
        """)
        staff_list = cur.fetchall()
        cur.close()
    except Exception as e:
        return handle_mysql_error(e, 'admin_bp.admin_staff_list')

    return render_template('admin/staff_list.html', staff=staff_list)
