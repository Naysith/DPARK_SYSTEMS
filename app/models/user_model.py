from flask import flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import mysql
from app.utils.error_handler import handle_mysql_error
from flask import current_app

# ---------------- AUTH ----------------
def login_user(form):
    email = form['email']
    password = form['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM pengguna WHERE email=%s", (email,))
    user = cur.fetchone()
    cur.close()

    if user and check_password_hash(user[3], password):
        session['id_pengguna'] = user[0]
        session['nama_pengguna'] = user[1]
        # Normalize role value and validate
        role = (user[4] or '').strip().lower() if len(user) > 4 else ''
        valid_roles = {'admin', 'staff', 'pelanggan'}
        if role not in valid_roles:
            current_app.logger.warning(f"Unexpected role for user {user[0]}: {user[4]!r} - defaulting to 'pelanggan'")
            role = 'pelanggan'
        session['peran'] = role

        flash('Login berhasil!', 'success')

        # ✅ Correct role-based routing
        if session['peran'] == 'admin':
            return redirect(url_for('admin_bp.admin_dashboard'))
        elif session['peran'] == 'pelanggan':
            return redirect(url_for('user_bp.user_dashboard'))
        else:
            return redirect(url_for('auth_bp.home'))

    flash('Email atau password salah!', 'danger')
    return redirect(url_for('auth_bp.login'))

def register_user(form):
    try:
        nama = form['nama_pengguna']
        email = form['email']
        password = generate_password_hash(form['password'])
        nomor = form.get('nomor_telepon')      # new
        alamat = form.get('alamat_rumah')      # new

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO pengguna (nama_pengguna, email, password_hash, peran, nomor_telepon, alamat_rumah)
            VALUES (%s, %s, %s, 'pelanggan', %s, %s)
        """, (nama, email, password, nomor, alamat))
        mysql.connection.commit()
        cur.close()

        flash('Akun berhasil dibuat! Silakan login.')
        return redirect(url_for('auth_bp.login'))

    except Exception as e:
        return handle_mysql_error(e, 'auth_bp.register')


def logout_user():
    session.clear()
    flash('Berhasil logout.')
    return redirect(url_for('auth_bp.home'))


# ---------------- USERS CRUD ----------------
def get_users(id=None, role=None):
    """Fetch users. If `id` is provided, return single user. If `role` is provided, filter by role."""
    try:
        cur = mysql.connection.cursor()
        if id:
            cur.execute("SELECT * FROM pengguna WHERE id_pengguna=%s", (id,))
            data = cur.fetchone()
        else:
            if role:
                cur.execute("SELECT id_pengguna, nama_pengguna, email, peran, nomor_telepon, alamat_rumah FROM pengguna WHERE peran=%s", (role,))
            else:
                cur.execute("SELECT id_pengguna, nama_pengguna, email, peran, nomor_telepon, alamat_rumah FROM pengguna")
            data = cur.fetchall()
        cur.close()
        return data

    except Exception as e:
        return handle_mysql_error(e, 'user_bp.users_list')


def add_user(form):
    try:
        nama = form['nama_pengguna']
        email = form['email']
        password = generate_password_hash(form['password'])
        peran = form['peran']
        nomor = form.get('nomor_telepon')
        alamat = form.get('alamat_rumah')
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO pengguna (nama_pengguna, email, password_hash, peran, nomor_telepon, alamat_rumah)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (nama, email, password, peran, nomor, alamat))
        mysql.connection.commit()
        cur.close()
        flash('User berhasil ditambahkan!')
        return redirect(url_for('user_bp.users_list'))

    except Exception as e:
        return handle_mysql_error(e, 'user_bp.users_add')


def edit_user(id, form):
    try:
        nama = form['nama_pengguna']
        email = form['email']
        peran = form['peran']
        nomor = form.get('nomor_telepon')
        alamat = form.get('alamat_rumah')
        password = form.get('password')
        cur = mysql.connection.cursor()
        if password:
            cur.execute("""
                UPDATE pengguna SET nama_pengguna=%s, email=%s, password_hash=%s, peran=%s,
                    nomor_telepon=%s, alamat_rumah=%s WHERE id_pengguna=%s
            """, (nama, email, generate_password_hash(password), peran, nomor, alamat, id))
        else:
            cur.execute("""
                UPDATE pengguna SET nama_pengguna=%s, email=%s, peran=%s,
                    nomor_telepon=%s, alamat_rumah=%s WHERE id_pengguna=%s
            """, (nama, email, peran, nomor, alamat, id))
        mysql.connection.commit()
        cur.close()
        flash('User diperbarui!')
        return redirect(url_for('user_bp.users_list'))

    except Exception as e:
        return handle_mysql_error(e, 'user_bp.users_edit')


def delete_user(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM pengguna WHERE id_pengguna=%s", (id,))
        mysql.connection.commit()
        cur.close()
        flash('User dihapus!')
        return redirect(url_for('user_bp.users_list'))

    except Exception as e:
        return handle_mysql_error(e, 'user_bp.users_list')
