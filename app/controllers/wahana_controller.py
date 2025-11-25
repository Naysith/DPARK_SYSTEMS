from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.wahana_model import get_wahana, add_wahana, edit_wahana, delete_wahana
from flask import send_file, abort, Response
from app.utils.helpers import login_required, role_required
from app.utils.error_handler import handle_mysql_error
from datetime import datetime, timedelta, time

wahana_bp = Blueprint('wahana_bp', __name__)

@wahana_bp.route('/wahana')
@login_required
@role_required('admin')
def wahana_list():
    try:
        wahana = get_wahana()
    except Exception as e:
        return handle_mysql_error(e, 'wahana_bp.wahana_list')
    return render_template('wahana/wahana_list.html', wahana=wahana)


@wahana_bp.route('/wahana/image/<int:id>')
@login_required
def wahana_image(id):
    try:
        w = get_wahana(id)
        if not w:
            abort(404)
        img = w[4]
        # If stored as filename, redirect to static file
        if isinstance(img, str) and img:
            return redirect(url_for('static', filename='uploads/' + img))
        # If stored as bytes/blob, stream it
        if isinstance(img, (bytes, bytearray)):
            return Response(img, mimetype='image/jpeg')
        abort(404)
    except Exception as e:
        return handle_mysql_error(e, 'wahana_bp.wahana_image')

@wahana_bp.route('/wahana/add', methods=['GET','POST'])
@login_required
@role_required('admin')
def wahana_add():
    if request.method == 'POST':
        try:
            add_wahana(request.form, request.files)
            flash('✅ Wahana berhasil ditambahkan!', 'success')
            return redirect(url_for('wahana_bp.wahana_list'))
        except Exception as e:
            return handle_mysql_error(e, 'wahana_bp.wahana_list')
    return render_template('wahana/wahana_form.html')

@wahana_bp.route('/wahana/edit/<int:id>', methods=['GET','POST'])
@login_required
@role_required('admin')
def wahana_edit(id):
    if request.method == 'POST':
        try:
            edit_wahana(id, request.form, request.files)
            flash('✅ Wahana berhasil diperbarui!', 'success')
            return redirect(url_for('wahana_bp.wahana_list'))
        except Exception as e:
            return handle_mysql_error(e, 'wahana_bp.wahana_list')
    try:
        wahana = get_wahana(id)
    except Exception as e:
        return handle_mysql_error(e, 'wahana_bp.wahana_list')
    return render_template('wahana/wahana_form.html', wahana=wahana)

@wahana_bp.route('/wahana/delete/<int:id>')
@login_required
@role_required('admin')
def wahana_delete(id):
    try:
        delete_wahana(id)
        flash('🗑️ Wahana berhasil dihapus!', 'info')
        return redirect(url_for('wahana_bp.wahana_list'))
    except Exception as e:
        return handle_mysql_error(e, 'wahana_bp.wahana_list')

DEFAULT_SESSION_PRICE = 50000

@wahana_bp.route("/generate-auto-sesi", methods=["POST"])
def generate_auto_sesi():
    from app import mysql
    cur = mysql.connection.cursor()

    # Fetch all wahana
    cur.execute("SELECT id_wahana, nama_wahana FROM wahana")
    wahana_list = cur.fetchall()

    today = datetime.now().date()
    end_date = today + timedelta(days=90)

    sessions_per_day = [
        ("Pagi", time(9, 0),  time(13, 0)),
        ("Siang", time(13, 0), time(17, 0)),
        ("Malam", time(17, 0), time(21, 0)),
    ]

    added_count = 0
    for w in wahana_list:
        id_wahana, nama_wahana = w
        date = today
        while date <= end_date:
            for sesi_name, start, end in sessions_per_day:
                start_dt = datetime.combine(date, start)
                end_dt = datetime.combine(date, end)

                # Skip if already exists
                cur.execute("""
                    SELECT id_sesi FROM sesi
                    WHERE id_wahana=%s AND waktu_mulai=%s
                """, (id_wahana, start_dt))
                if cur.fetchone():
                    continue

                cur.execute("""
                    INSERT INTO sesi (id_wahana, nama_sesi, kuota, harga, waktu_mulai, waktu_selesai)
                    VALUES (%s,%s,%s,%s,%s,%s)
                """, (id_wahana, sesi_name, 50, DEFAULT_SESSION_PRICE, start_dt, end_dt))
                added_count += 1
            date += timedelta(days=1)

    mysql.connection.commit()
    cur.close()
    print(f"✅ Generated {added_count} sessions with default price Rp {DEFAULT_SESSION_PRICE:,}.")  # run your function
    flash("Sesi berhasil dibuat otomatis!", "success")
    return redirect(url_for("wahana_bp.wahana_list"))