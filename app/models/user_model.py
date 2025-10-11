from flask import flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import mysql

# ---------------- AUTH ----------------
def login_user(form):
    email = form['email']
    password = form['password']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    cur.close()

    if user and check_password_hash(user[3], password):
        session['id_pengguna'] = user[0]
        session['nama_pengguna'] = user[1]
        session['peran'] = user[4]
        flash('Login berhasil!')
        if user[4] == 'admin':
            return redirect(url_for('admin_bp.admin_dashboard'))
        elif user[4] == 'staff':
            return redirect(url_for('staff_bp.validasi'))
        else:
            return redirect(url_for('reservasi_bp.reservasi_list'))

    flash('Email atau password salah!')
    return redirect(url_for('auth_bp.login'))

def register_user(form):
    nama = form['nama_pengguna']
    email = form['email']
    password = generate_password_hash(form['password'])
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO users (nama_pengguna, email, password_hash, peran)
        VALUES (%s, %s, %s, 'pelanggan')
    """, (nama, email, password))
    mysql.connection.commit()
    cur.close()
    flash('Akun berhasil dibuat! Silakan login.')
    return redirect(url_for('auth_bp.login'))

def logout_user():
    session.clear()
    flash('Berhasil logout.')
    return redirect(url_for('auth_bp.home'))

# ---------------- USERS CRUD ----------------
def get_users(id=None):
    cur = mysql.connection.cursor()
    if id:
        cur.execute("SELECT * FROM users WHERE id_pengguna=%s", (id,))
        data = cur.fetchone()
    else:
        cur.execute("SELECT id_pengguna, nama_pengguna, email, peran, nomor_telepon, alamat_rumah FROM users")
        data = cur.fetchall()
    cur.close()
    return data

def add_user(form):
    nama = form['nama_pengguna']
    email = form['email']
    password = generate_password_hash(form['password'])
    peran = form['peran']
    nomor = form.get('nomor_telepon')
    alamat = form.get('alamat_rumah')
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO users (nama_pengguna, email, password_hash, peran, nomor_telepon, alamat_rumah)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (nama, email, password, peran, nomor, alamat))
    mysql.connection.commit()
    cur.close()
    flash('User berhasil ditambahkan!')
    return redirect(url_for('user_bp.users_list'))

def edit_user(id, form):
    nama = form['nama_pengguna']
    email = form['email']
    peran = form['peran']
    nomor = form.get('nomor_telepon')
    alamat = form.get('alamat_rumah')
    password = form.get('password')
    cur = mysql.connection.cursor()
    if password:
        cur.execute("""
            UPDATE users SET nama_pengguna=%s, email=%s, password_hash=%s, peran=%s,
                nomor_telepon=%s, alamat_rumah=%s WHERE id_pengguna=%s
        """, (nama, email, generate_password_hash(password), peran, nomor, alamat, id))
    else:
        cur.execute("""
            UPDATE users SET nama_pengguna=%s, email=%s, peran=%s,
                nomor_telepon=%s, alamat_rumah=%s WHERE id_pengguna=%s
        """, (nama, email, peran, nomor, alamat, id))
    mysql.connection.commit()
    cur.close()
    flash('User diperbarui!')
    return redirect(url_for('user_bp.users_list'))

def delete_user(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id_pengguna=%s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('User dihapus!')
    return redirect(url_for('user_bp.users_list'))
