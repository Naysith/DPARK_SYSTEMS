from flask import render_template, request, redirect, url_for, flash, session
from app import app
from functions import (
    login_user, register_user, logout_user,
    get_users, add_user, edit_user, delete_user,
    get_wahana, add_wahana,
    get_sesi, add_sesi,
    get_reservasi, add_reservasi,
    add_pembayaran,
    get_tiket, validate_tiket
)
from functions import login_required, role_required

# ---------------- AUTH ----------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return login_user(request.form)
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return register_user(request.form)
    return render_template('register.html')

@app.route('/logout')
def logout():
    return logout_user()


# ---------------- USERS ----------------
@app.route('/users')
@login_required
@role_required('admin')
def users_list():
    users = get_users()
    return render_template('users/list.html', users=users)

@app.route('/users/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def users_add():
    if request.method == 'POST':
        return add_user(request.form)
    return render_template('users/form.html')

@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def users_edit(id):
    if request.method == 'POST':
        return edit_user(id, request.form)
    user = get_users(id)
    return render_template('users/form.html', user=user)

@app.route('/users/delete/<int:id>')
@login_required
@role_required('admin')
def users_delete(id):
    return delete_user(id)


# ---------------- ADMIN DASHBOARD ----------------
@app.route('/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')


# ---------------- WAHANA ----------------
@app.route('/wahana')
@login_required
def wahana_list():
    wahana = get_wahana()
    return render_template('wahana/list.html', wahana=wahana)

@app.route('/wahana/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def wahana_add():
    if request.method == 'POST':
        return add_wahana(request.form, request.files)
    return render_template('wahana/form.html')


# ---------------- SESI ----------------
@app.route('/sesi')
@login_required
@role_required('admin')
def sesi_list():
    data = get_sesi()
    return render_template('sesi_list.html', sesi=data)

@app.route('/sesi/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def sesi_add():
    if request.method == 'POST':
        return add_sesi(request.form)
    wahana_data = get_wahana()
    return render_template('sesi_add.html', wahana=wahana_data)


# ---------------- RESERVASI ----------------
@app.route('/reservasi')
@login_required
def reservasi_list():
    data = get_reservasi(session)
    return render_template('reservasi/reservasi_list.html', reservasi=data)

@app.route('/reservasi/add', methods=['GET', 'POST'])
@login_required
def reservasi_add():
    if request.method == 'POST':
        return add_reservasi(request.form, session)
    # for GET → show form with available sesi
    sesi_data = get_sesi(available_only=True)
    return render_template('reservasi/reservasi_add.html', sesi=sesi_data)


# ---------------- PEMBAYARAN ----------------
@app.route('/pembayaran/add/<int:id>', methods=['GET', 'POST'])
@login_required
def pembayaran_add(id):
    if request.method == 'POST':
        return add_pembayaran(id, request.form)
    return render_template('pembayaran/form.html')


# ---------------- TIKET ----------------
@app.route('/tiket')
@login_required
def tiket_list():
    tiket = get_tiket(session)
    return render_template('tiket/list.html', tiket=tiket)


# ---------------- VALIDASI (STAFF) ----------------
@app.route('/validasi', methods=['GET', 'POST'])
@login_required
@role_required('staff')
def validasi():
    if request.method == 'POST':
        return validate_tiket(request.form, session)
    return render_template('staff/validasi.html')
