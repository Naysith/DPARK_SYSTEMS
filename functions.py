from flask import flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from uuid import uuid4
from datetime import datetime
import os
from app import mysql

# ===============================
# Helpers / Decorators
# ===============================
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'id_pengguna' not in session:
            flash('Please login first.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'peran' not in session or session['peran'] not in roles:
                flash('Access denied.')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return wrapper
    return decorator

def parse_datetime_local(value):
    if not value:
        return None
    v = value.replace('T', ' ')
    if len(v) == 16:
        v += ":00"
    return v

def generate_code(prefix="", length=8):
    return prefix + uuid4().hex[:length]


# ===============================
# AUTH FUNCTIONS
# ===============================
def login_user(form):
    email = form['email']
    password = form['password']
    print("LOGIN DEBUG:", email, password)
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    print("USER DATA:", user)
    cur.close()
    if user and check_password_hash(user[3], password):
        session['id_pengguna'] = user[0]
        session['nama_pengguna'] = user[1]
        session['peran'] = user[4]
        flash('Login berhasil!')
        if user[4] == 'admin':
            return redirect(url_for('users_list'))
        elif user[4] == 'staff':
            return redirect(url_for('validasi'))
        else:
            return redirect(url_for('reservasi_list'))
    flash('Email atau password salah!')
    return redirect(url_for('login'))

def register_user(form):
    nama = form['nama_pengguna']
    email = form['email']
    password = generate_password_hash(form['password'])
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO users (nama_pengguna, email, password_hash, peran)
        VALUES (%s,%s,%s,%s)
    """, (nama, email, password, 'pelanggan'))
    mysql.connection.commit()
    cur.close()
    flash('Akun berhasil dibuat!')
    return redirect(url_for('login'))

def logout_user():
    session.clear()
    flash('Berhasil logout.')
    return redirect(url_for('index'))


# ===============================
# USERS CRUD (ADMIN)
# ===============================
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
    return redirect(url_for('users_list'))

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
    return redirect(url_for('users_list'))

def delete_user(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id_pengguna=%s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('User dihapus!')
    return redirect(url_for('users_list'))


# ===============================
# WAHANA CRUD
# ===============================
def get_wahana(id=None):
    cur = mysql.connection.cursor()
    if id:
        cur.execute("SELECT * FROM wahana WHERE id_wahana=%s", (id,))
        data = cur.fetchone()
    else:
        cur.execute("SELECT * FROM wahana")
        data = cur.fetchall()
    cur.close()
    return data

def add_wahana(form, files):
    nama = form['nama_wahana']
    deskripsi = form['deskripsi']
    status = form['status_wahana']
    gambar = files.get('gambar_wahana')
    filename = None
    if gambar and allowed_file(gambar.filename):
        filename = secure_filename(f"{uuid4().hex}_{gambar.filename}")
        gambar.save(os.path.join('static/uploads', filename))
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO wahana (nama_wahana, deskripsi, status_wahana, gambar_wahana)
        VALUES (%s,%s,%s,%s)
    """, (nama, deskripsi, status, filename))
    mysql.connection.commit()
    cur.close()
    flash('Wahana ditambahkan!')
    return redirect(url_for('wahana_list'))


# ===============================
# SESI CRUD
# ===============================
def get_sesi(available_only=False):
    cur = mysql.connection.cursor()
    if available_only:
        cur.execute("""
            SELECT id_sesi, nama_sesi, kuota, harga FROM sesi WHERE kuota > 0
        """)
    else:
        cur.execute("""
            SELECT s.id_sesi, s.nama_sesi, s.kuota, s.harga, s.waktu_mulai, s.waktu_selesai, w.nama_wahana
            FROM sesi s JOIN wahana w ON s.id_wahana=w.id_wahana
        """)
    data = cur.fetchall()
    cur.close()
    return data

def add_sesi(form):
    id_wahana = form['id_wahana']
    nama_sesi = form['nama_sesi']
    kuota = form['kuota']
    harga = form['harga']
    waktu_mulai = parse_datetime_local(form['waktu_mulai'])
    waktu_selesai = parse_datetime_local(form['waktu_selesai'])
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO sesi (id_wahana, nama_sesi, kuota, harga, waktu_mulai, waktu_selesai)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (id_wahana, nama_sesi, kuota, harga, waktu_mulai, waktu_selesai))
    mysql.connection.commit()
    cur.close()
    flash('Sesi ditambahkan!')
    return redirect(url_for('sesi_list'))


# ===============================
# RESERVASI
# ===============================
def get_reservasi(sess):
    cur = mysql.connection.cursor()
    if sess['peran'] == 'admin':
        cur.execute("""
            SELECT r.id_reservasi, u.nama_pengguna, r.total_harga, r.status_pembayaran, r.tanggal_reservasi
            FROM reservasi r JOIN users u ON r.id_pengguna=u.id_pengguna ORDER BY r.tanggal_reservasi DESC
        """)
    else:
        cur.execute("""
            SELECT id_reservasi, total_harga, status_pembayaran, tanggal_reservasi
            FROM reservasi WHERE id_pengguna=%s ORDER BY tanggal_reservasi DESC
        """, (sess['id_pengguna'],))
    data = cur.fetchall()
    cur.close()
    return data

def add_reservasi(form, sess):
    id_pengguna = sess['id_pengguna']
    id_sesi = form['id_sesi']
    jumlah = int(form['jumlah'])
    kode_unik = generate_code('R-', 8)
    cur = mysql.connection.cursor()
    cur.execute("SELECT harga, kuota FROM sesi WHERE id_sesi=%s", (id_sesi,))
    s = cur.fetchone()
    if not s or s[1] < jumlah:
        flash('Kuota tidak cukup!', 'danger')
        return redirect(url_for('reservasi_add'))
    total = s[0] * jumlah
    cur.execute("""
        INSERT INTO reservasi (id_pengguna, total_harga, status_pembayaran, kode_unik)
        VALUES (%s,%s,'menunggu',%s)
    """, (id_pengguna, total, kode_unik))
    reservasi_id = cur.lastrowid
    for i in range(jumlah):
        kode_tiket = generate_code('T-', 10)
        cur.execute("""
            INSERT INTO tiket (id_reservasi, id_sesi, kode_tiket)
            VALUES (%s,%s,%s)
        """, (reservasi_id, id_sesi, kode_tiket))
    cur.execute("UPDATE sesi SET kuota = kuota - %s WHERE id_sesi=%s", (jumlah, id_sesi))
    mysql.connection.commit()
    cur.close()
    flash('Reservasi berhasil dibuat!')
    return redirect(url_for('reservasi_list'))


# ===============================
# PEMBAYARAN
# ===============================
def add_pembayaran(id_reservasi, form):
    jumlah = form['jumlah_bayar']
    metode = form['metode_pembayaran']
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO pembayaran (id_reservasi, jumlah_bayar, metode_pembayaran)
        VALUES (%s,%s,%s)
    """, (id_reservasi, jumlah, metode))
    cur.execute("UPDATE reservasi SET status_pembayaran='selesai' WHERE id_reservasi=%s", (id_reservasi,))
    mysql.connection.commit()
    cur.close()
    flash('Pembayaran berhasil!')
    return redirect(url_for('reservasi_list'))


# ===============================
# TIKET & VALIDASI
# ===============================
def get_tiket(sess):
    cur = mysql.connection.cursor()
    if sess['peran'] == 'admin':
        cur.execute("""
            SELECT t.kode_tiket, t.status_tiket, w.nama_wahana, s.nama_sesi
            FROM tiket t
            JOIN sesi s ON t.id_sesi=s.id_sesi
            JOIN wahana w ON s.id_wahana=w.id_wahana
        """)
    else:
        cur.execute("""
            SELECT t.kode_tiket, t.status_tiket, w.nama_wahana, s.nama_sesi
            FROM tiket t
            JOIN reservasi r ON t.id_reservasi=r.id_reservasi
            JOIN sesi s ON t.id_sesi=s.id_sesi
            JOIN wahana w ON s.id_wahana=w.id_wahana
            WHERE r.id_pengguna=%s
        """, (sess['id_pengguna'],))
    data = cur.fetchall()
    cur.close()
    return data

def validate_tiket(form, sess):
    kode = form['kode_tiket']
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT t.id_tiket, t.status_tiket, s.id_wahana
        FROM tiket t JOIN sesi s ON t.id_sesi=s.id_sesi
        WHERE t.kode_tiket=%s
    """, (kode,))
    t = cur.fetchone()
    if not t:
        flash('Tiket tidak ditemukan!', 'danger')
    elif t[1] == 'sudah_digunakan':
        flash('Tiket sudah digunakan!', 'warning')
    else:
        cur.execute("UPDATE tiket SET status_tiket='sudah_digunakan' WHERE id_tiket=%s", (t[0],))
        cur.execute("INSERT INTO validasi (id_pengguna, id_wahana) VALUES (%s,%s)", (sess['id_pengguna'], t[2]))
        mysql.connection.commit()
        flash('Tiket berhasil divalidasi!', 'success')
    cur.close()
    return redirect(url_for('validasi'))
