from flask import Blueprint, jsonify, render_template, request, flash, redirect, url_for, session
from app import mysql
from app.utils.helpers import login_required, role_required
from app.utils.error_handler import handle_mysql_error
from werkzeug.security import generate_password_hash, check_password_hash


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

@staff_bp.route('/staff/profile')
@login_required
@role_required('staff')
def profile():
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
        handle_mysql_error(e, 'staff_bp.profile')
        flash('Gagal memuat profil.', 'danger')
        user = None

    return render_template('staff/profile_setting.html', user=user)

@staff_bp.route('/staff/validasi_tiket', methods=['GET', 'POST'])
@login_required
@role_required('staff')
def validasi_tiket():
    result = None
    validasi_list = []
    try:
        cur = mysql.connection.cursor()

        # --- Changed: fetch validated tickets directly from tiket/reservasi/sesi/wahana
        # Select latest validation time for the wahana using a correlated subquery to avoid row multiplication.
        cur.execute("""
            SELECT
                t.kode_tiket,
                u.nama_pengguna,
                w.nama_wahana,
                (
                    SELECT MAX(v.waktu_validasi)
                    FROM validasi v
                    WHERE v.id_wahana = w.id_wahana
                ) AS waktu_validasi
            FROM tiket t
            JOIN sesi s ON t.id_sesi = s.id_sesi
            JOIN wahana w ON s.id_wahana = w.id_wahana
            JOIN reservasi r ON t.id_reservasi = r.id_reservasi
            JOIN pengguna u ON r.id_pengguna = u.id_pengguna
            WHERE t.status_tiket = 'sudah_digunakan'
            GROUP BY t.id_tiket, t.kode_tiket, u.nama_pengguna, w.nama_wahana
            ORDER BY waktu_validasi DESC
            LIMIT 100
        """)
        validasi_list = cur.fetchall()

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

                # Refresh the recent list using the same stable query (avoid multiplication)
                cur.execute("""
                    SELECT
                        t.kode_tiket,
                        u.nama_pengguna,
                        w.nama_wahana,
                        (
                            SELECT MAX(v.waktu_validasi)
                            FROM validasi v
                            WHERE v.id_wahana = w.id_wahana
                        ) AS waktu_validasi
                    FROM tiket t
                    JOIN sesi s ON t.id_sesi = s.id_sesi
                    JOIN wahana w ON s.id_wahana = w.id_wahana
                    JOIN reservasi r ON t.id_reservasi = r.id_reservasi
                    JOIN pengguna u ON r.id_pengguna = u.id_pengguna
                    WHERE t.status_tiket = 'sudah_digunakan'
                    GROUP BY t.id_tiket, t.kode_tiket, u.nama_pengguna, w.nama_wahana
                    ORDER BY waktu_validasi DESC
                    LIMIT 100
                """)
                validasi_list = cur.fetchall()

        cur.close()
    except Exception as e:
        handle_mysql_error(e, 'staff_bp.validasi_tiket')
        flash('Terjadi kesalahan saat memproses tiket.', 'danger')

    return render_template('staff/validasi_tiket.html', result=result, validasi_list=validasi_list)

@staff_bp.route('/staff/profile/update_contact', methods=['POST'])
@login_required
@role_required('staff')
def update_profile_contact():
    try:
        data = request.get_json() or {}
        nomor = (data.get('nomor_telepon') or '').strip()
        alamat = (data.get('alamat_rumah') or '').strip()
        id_pengguna = session.get('id_pengguna')
        if not id_pengguna:
            return jsonify(success=False, message='User tidak terautentikasi'), 401

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE pengguna SET nomor_telepon=%s, alamat_rumah=%s WHERE id_pengguna=%s
        """, (nomor, alamat, id_pengguna))
        mysql.connection.commit()
        cur.close()

        session['nomor_telepon'] = nomor
        session['alamat_rumah'] = alamat
        return jsonify(success=True, message='Informasi kontak berhasil diperbarui',
                       nomor_telepon=nomor, alamat_rumah=alamat)
    except Exception as e:
        handle_mysql_error(e, 'staff_bp.update_profile_contact')
        return jsonify(success=False, message='Gagal menyimpan informasi kontak'), 500

@staff_bp.route('/staff/profile/update_account', methods=['POST'])
@login_required
@role_required('staff')
def update_profile_account():
    try:
        data = request.get_json() or {}
        nama = (data.get('nama_pengguna') or '').strip()
        password = data.get('password')  # kosong => tidak berubah
        old_password = data.get('old_password')
        id_pengguna = session.get('id_pengguna')
        if not id_pengguna:
            return jsonify(success=False, message='User tidak terautentikasi'), 401

        cur = mysql.connection.cursor()
        # ambil hash password saat ini dari kolom password_hash
        cur.execute("SELECT password_hash FROM pengguna WHERE id_pengguna=%s", (id_pengguna,))
        row = cur.fetchone()
        current_pw = row[0] if row else None

        # pastikan current_pw text bukan bytes
        if isinstance(current_pw, (bytes, bytearray)):
            try:
                current_pw = current_pw.decode('utf-8')
            except Exception:
                current_pw = str(current_pw)

        if password:  # user ingin mengubah password
            if not old_password:
                cur.close()
                return jsonify(success=False, message='Password lama harus diisi untuk mengganti password'), 400

            # current_pw harus berupa hash, cek menggunakan check_password_hash
            pw_ok = False
            if current_pw:
                try:
                    pw_ok = check_password_hash(current_pw, old_password)
                except Exception as ex:
                    print(f"[DEBUG] check_password_hash error: {ex}")
                    pw_ok = False

            if not pw_ok:
                cur.close()
                return jsonify(success=False, message='Password lama tidak cocok'), 403

            pwd_hash = generate_password_hash(password)
            # simpan ke kolom password_hash
            cur.execute("UPDATE pengguna SET nama_pengguna=%s, password_hash=%s WHERE id_pengguna=%s",
                        (nama, pwd_hash, id_pengguna))
        else:
            cur.execute("UPDATE pengguna SET nama_pengguna=%s WHERE id_pengguna=%s", (nama, id_pengguna))

        mysql.connection.commit()
        cur.close()

        session['nama_pengguna'] = nama
        return jsonify(success=True, message='Informasi akun berhasil diperbarui', nama_pengguna=nama)
    except Exception as e:
        import traceback
        traceback.print_exc()
        handle_mysql_error(e, 'staff_bp.update_profile_account')
        return jsonify(success=False, message=f'Gagal menyimpan informasi akun: {str(e)}'), 500


@staff_bp.route('/api/staff/cek_tiket', methods=['POST'])
@login_required
@role_required('staff')
def api_cek_tiket():
    try:
        data = request.get_json() or request.form
        kode_tiket = data.get('kode_tiket')
        if not kode_tiket:
            return jsonify(success=False, message='Kode tiket harus diisi'), 400

        cur = mysql.connection.cursor()
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
                w.nama_wahana,
                u.nama_pengguna
            FROM tiket t
            JOIN sesi s ON t.id_sesi = s.id_sesi
            JOIN wahana w ON s.id_wahana = w.id_wahana
            JOIN reservasi r ON t.id_reservasi = r.id_reservasi
            JOIN pengguna u ON r.id_pengguna = u.id_pengguna
            WHERE t.kode_tiket = %s
        """, (kode_tiket,))
        row = cur.fetchone()
        cur.close()

        if not row:
            return jsonify(success=False, message='Kode tiket tidak ditemukan'), 404

        # pack result
        result = {
            'id_tiket': row[0],
            'kode_tiket': row[1],
            'status_tiket': row[2],
            'id_sesi': row[3],
            'nama_sesi': row[4],
            'waktu_mulai': row[5].isoformat() if hasattr(row[5], 'isoformat') else row[5],
            'waktu_selesai': row[6].isoformat() if hasattr(row[6], 'isoformat') else row[6],
            'id_wahana': row[7],
            'nama_wahana': row[8],
            'nama_pengguna': row[9]
        }
        return jsonify(success=True, data=result)
    except Exception as e:
        handle_mysql_error(e, 'staff_bp.api_cek_tiket')
        return jsonify(success=False, message='Terjadi kesalahan server'), 500

@staff_bp.route('/api/staff/validasi', methods=['POST'])
@login_required
@role_required('staff')
def api_validasi():
    try:
        data = request.get_json() or request.form
        id_tiket = data.get('id_tiket')
        id_wahana = data.get('id_wahana')
        id_pengguna = session.get('id_pengguna')

        if not id_tiket or not id_wahana:
            return jsonify(success=False, message='Data validasi tidak lengkap'), 400

        cur = mysql.connection.cursor()
        # update tiket
        cur.execute("""
            UPDATE tiket 
            SET status_tiket = 'sudah_digunakan'
            WHERE id_tiket = %s
        """, (id_tiket,))

        # insert log validasi
        cur.execute("""
            INSERT INTO validasi (id_pengguna, id_wahana)
            VALUES (%s, %s)
        """, (id_pengguna, id_wahana))

        mysql.connection.commit()
        cur.close()

        return jsonify(success=True, message='Tiket berhasil divalidasi')
    except Exception as e:
        handle_mysql_error(e, 'staff_bp.api_validasi')
        return jsonify(success=False, message='Terjadi kesalahan saat memvalidasi'), 500

