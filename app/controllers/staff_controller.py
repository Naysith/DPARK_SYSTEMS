from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from app import mysql
from app.utils.helpers import login_required, role_required
from app.utils.error_handler import handle_mysql_error

staff_bp = Blueprint('staff_bp', __name__)

@staff_bp.route('/staff/dashboard')
@login_required
@role_required('staff')
def staff_dashboard():
    try:
        cur = mysql.connection.cursor()
        id_staff = session.get('id_pengguna')

        # Ambil total validasi oleh staff ini
        cur.execute("""
            SELECT COUNT(*) 
            FROM validasi 
            WHERE id_pengguna = %s
        """, (id_staff,))
        total_validasi = cur.fetchone()[0]

        # Ambil validasi hari ini oleh staff ini
        cur.execute("""
            SELECT COUNT(*) 
            FROM validasi 
            WHERE id_pengguna = %s AND DATE(waktu_validasi) = CURDATE()
        """, (id_staff,))
        validasi_hari_ini = cur.fetchone()[0]

        # Ambil log validasi terakhir (10 entri)
        cur.execute("""
            SELECT 
                v.id_validasi,
                w.nama_wahana,
                v.waktu_validasi
            FROM validasi v
            JOIN wahana w ON v.id_wahana = w.id_wahana
            WHERE v.id_pengguna = %s
            ORDER BY v.waktu_validasi DESC
            LIMIT 10
        """, (id_staff,))
        validasi_list = cur.fetchall()

        cur.close()

    except Exception as e:
        return handle_mysql_error(e, 'staff_bp.staff_dashboard')

    return render_template(
        'staff/staff_dashboard.html',
        total_validasi=total_validasi,
        validasi_hari_ini=validasi_hari_ini,
        validasi_list=validasi_list
    )

@staff_bp.route('/staff/validasi_tiket', methods=['GET', 'POST'])
@login_required
@role_required('staff')
def validasi_tiket():
    result = None
    try:
        cur = mysql.connection.cursor()

        if request.method == 'POST':
            if 'cari' in request.form:
                kode_tiket = request.form.get('kode_tiket')

                if not kode_tiket:
                    flash('Kode tiket harus diisi.', 'danger')
                else:
                    cur.execute("""
                        SELECT 
                            t.id_tiket,
                            t.kode_tiket,
                            t.status_tiket,
                            s.id_sesi,
                            s.nama_sesi,
                            s.waktu_mulai,
                            s.waktu_selesai,
                            w.id_wahana,
                            w.nama_wahana
                        FROM tiket t
                        JOIN sesi s ON t.id_sesi = s.id_sesi
                        JOIN wahana w ON s.id_wahana = w.id_wahana
                        WHERE t.kode_tiket = %s
                    """, (kode_tiket,))
                    result = cur.fetchone()

                    if not result:
                        flash('Kode tiket tidak ditemukan.', 'danger')
                    elif result[2] == 'sudah_digunakan':
                        flash('Tiket ini sudah digunakan sebelumnya.', 'warning')

            elif 'validasi' in request.form:
                id_tiket = request.form.get('id_tiket')
                id_wahana = request.form.get('id_wahana')
                id_pengguna = session.get('id_pengguna')  # staff ID

                # 1️⃣ Update tiket status
                cur.execute("""
                    UPDATE tiket 
                    SET status_tiket = 'sudah_digunakan'
                    WHERE id_tiket = %s
                """, (id_tiket,))

                # 2️⃣ Insert into validasi log
                cur.execute("""
                    INSERT INTO validasi (id_pengguna, id_wahana)
                    VALUES (%s, %s)
                """, (id_pengguna, id_wahana))

                mysql.connection.commit()
                flash('Tiket berhasil divalidasi dan dicatat di log validasi.', 'success')
                result = None

        cur.close()
    except Exception as e:
        handle_mysql_error(e, 'staff_bp.validasi_tiket')
        flash('Terjadi kesalahan saat memproses tiket.', 'danger')

    return render_template('staff/validasi_tiket.html', result=result)

