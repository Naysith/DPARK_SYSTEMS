from flask import flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import mysql

# ----------------------------
# USER AUTH LOGIC (MODEL)
# ----------------------------

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

        # Redirect based on role
        if user[4] == 'admin':
            return redirect(url_for('admin_bp.admin_dashboard'))
        elif user[4] == 'staff':
            return redirect(url_for('staff_bp.validasi'))
        elif user[4] == 'admin':
            return redirect(url_for('admin_bp.admin_dashboard'))
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



