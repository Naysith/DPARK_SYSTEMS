from flask import Blueprint, render_template, request, session
from app.utils.helpers import login_required, role_required
from app.models.user_model import get_users, add_user, edit_user, delete_user
from app.utils.error_handler import handle_mysql_error
from app.models.wahana_model import get_wahana, get_all_wahana
from app.models.reservasi_model import add_reservasi_return_id
from datetime import datetime, timedelta
from flask import request, redirect, url_for, session, render_template, flash

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/user')
@login_required
@role_required('pelanggan')
def user_dashboard():
    from app.models.reservasi_model import get_reservasi_by_user
    from app.models.tiket_model import get_tiket
    reservasi = get_reservasi_by_user(session.get('id_pengguna'))
    tiket = get_tiket(session)
    return render_template('user/user_dashboard.html', reservasi=reservasi, tiket=tiket)


@user_bp.route('/user/reservasi/start')
@login_required
@role_required('pelanggan')
def reservasi_start():
    # show list of wahana with image/title/desc
    wahana = get_all_wahana()
    return render_template('user/select_wahana.html', wahana=wahana)


@user_bp.route('/user/reservasi/list')
@login_required
@role_required('pelanggan')
def user_reservasi_list():
    from app.models.reservasi_model import get_reservasi_by_user
    try:
        reservasi = get_reservasi_by_user(session.get('id_pengguna'))
    except Exception as e:
        from app.utils.error_handler import handle_mysql_error
        return handle_mysql_error(e, 'user_bp.user_reservasi_list')
    return render_template('reservasi/reservasi_list.html', reservasi=reservasi)


@user_bp.route('/user/reservasi/select_date/<int:id_wahana>')
@login_required
@role_required('pelanggan')
def reservasi_select_date(id_wahana):
    # show next 14 days as selectable list
    days = [(datetime.now().date() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(14)]
    return render_template('user/select_date.html', id_wahana=id_wahana, days=days)


@user_bp.route('/user/reservasi/select_session', methods=['POST'])
@login_required
@role_required('pelanggan')
def reservasi_select_session():
    id_wahana = request.form.get('id_wahana')
    selected_date = request.form.get('selected_date')
    # provide pagi/siang/malam options
    sessions = [
        ('Pagi', '09:00'),
        ('Siang', '13:00'),
        ('Malam', '17:00')
    ]
    return render_template('user/select_session.html', id_wahana=id_wahana, selected_date=selected_date, sessions=sessions)


@user_bp.route('/user/reservasi/confirm', methods=['POST'])
@login_required
@role_required('pelanggan')
def reservasi_confirm():
    id_wahana = int(request.form.get('id_wahana'))
    date = request.form.get('selected_date')
    session_label = request.form.get('session_label')
    # map session_label to session time slot: find a sesi for that wahana and datetime
    # naive mapping: pick sesi by waktu_mulai matching the session start time on selected date
    waktu_str = None
    if session_label == 'Pagi':
        waktu_str = date + ' 09:00:00'
    elif session_label == 'Siang':
        waktu_str = date + ' 13:00:00'
    else:
        waktu_str = date + ' 17:00:00'

    # find matching sesi id
    cur = None
    try:
        from app import mysql
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_sesi FROM sesi WHERE id_wahana=%s AND DATE(waktu_mulai)=%s AND TIME(waktu_mulai)=%s", (id_wahana, date, waktu_str.split()[1]))
        row = cur.fetchone()
        if not row:
            flash('Sesi tidak ditemukan untuk pilihan tersebut.', 'danger')
            return redirect(url_for('user_bp.reservasi_start'))
        id_sesi = row[0]

        id_pengguna = session.get('id_pengguna')
        new_id = add_reservasi_return_id(id_pengguna, id_sesi, 1)
        if not new_id:
            flash('Gagal membuat reservasi. Silakan coba lagi.', 'danger')
            return redirect(url_for('user_bp.reservasi_start'))

        flash('Reservasi berhasil dibuat! Silakan lanjut ke pembayaran.', 'success')
        return redirect(url_for('reservasi_bp.pembayaran_form', id_reservasi=new_id))
    finally:
        if cur:
            cur.close()

@user_bp.route('/users')
@login_required
@role_required('admin')
def users_list():
    try:
        role = request.args.get('role')
        users = get_users(role=role)
    except Exception as e:
        return handle_mysql_error(e, 'user_bp.users_list')
    return render_template('users/list.html', users=users, current_role=role)

@user_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def users_add():
    if request.method == 'POST':
        try:
            return add_user(request.form)
        except Exception as e:
            return handle_mysql_error(e, 'user_bp.users_list')
    return render_template('users/form.html')

@user_bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def users_edit(id):
    if request.method == 'POST':
        try:
            return edit_user(id, request.form)
        except Exception as e:
            return handle_mysql_error(e, 'user_bp.users_list')
    try:
        user = get_users(id)
    except Exception as e:
        return handle_mysql_error(e, 'user_bp.users_list')
    return render_template('users/form.html', user=user)

@user_bp.route('/users/delete/<int:id>')
@login_required
@role_required('admin')
def users_delete(id):
    try:
        return delete_user(id)
    except Exception as e:
        return handle_mysql_error(e, 'user_bp.users_list')
