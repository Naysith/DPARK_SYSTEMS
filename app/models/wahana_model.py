from app import mysql
from werkzeug.utils import secure_filename
from uuid import uuid4
import os
from flask import flash, redirect, url_for
from app.utils.error_handler import handle_mysql_error

UPLOAD_FOLDER = 'app/static/uploads'

def check_duplicate(cur, column, value, exclude_id=None):
    sql = f"SELECT id_wahana FROM wahana WHERE {column}=%s"
    params = [value]
    if exclude_id:
        sql += " AND id_wahana != %s"
        params.append(exclude_id)
    cur.execute(sql, params)
    return cur.fetchone() is not None

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
    try:
        cur = mysql.connection.cursor()
        if check_duplicate(cur, 'nama_wahana', form['nama_wahana']):
            flash("❌ Wahana sudah ada!", "danger")
            return redirect(url_for('wahana_bp.wahana_add'))

        nama = form['nama_wahana']
        deskripsi = form['deskripsi']
        status = form['status_wahana']
        gambar = files.get('gambar_wahana')
        filename = None

        if gambar and allowed_file(gambar.filename):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = secure_filename(f"{uuid4().hex}_{gambar.filename}")
            gambar.save(os.path.join(UPLOAD_FOLDER, filename))

        cur.execute("""
            INSERT INTO wahana (nama_wahana, deskripsi, status_wahana, gambar_wahana)
            VALUES (%s, %s, %s, %s)
        """, (nama, deskripsi, status, filename))
        mysql.connection.commit()
        cur.close()
        flash('Wahana berhasil ditambahkan!', 'success')
        return redirect(url_for('wahana_bp.wahana_list'))
    except Exception as e:
        return handle_mysql_error(e, 'wahana_bp.wahana_add')

def edit_wahana(id, form, files):
    try:
        cur = mysql.connection.cursor()
        if check_duplicate(cur, 'nama_wahana', form['nama_wahana'], exclude_id=id):
            flash("❌ Nama wahana sudah digunakan!", "danger")
            return redirect(url_for('wahana_bp.wahana_edit', id=id))

        nama = form['nama_wahana']
        deskripsi = form['deskripsi']
        status = form['status_wahana']
        gambar = files.get('gambar_wahana')
        filename = None

        if gambar and allowed_file(gambar.filename):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = secure_filename(f"{uuid4().hex}_{gambar.filename}")
            gambar.save(os.path.join(UPLOAD_FOLDER, filename))

        if filename:
            cur.execute("""
                UPDATE wahana SET nama_wahana=%s, deskripsi=%s, status_wahana=%s, gambar_wahana=%s
                WHERE id_wahana=%s
            """, (nama, deskripsi, status, filename, id))
        else:
            cur.execute("""
                UPDATE wahana SET nama_wahana=%s, deskripsi=%s, status_wahana=%s
                WHERE id_wahana=%s
            """, (nama, deskripsi, status, id))

        mysql.connection.commit()
        cur.close()
        flash('Wahana diperbarui!', 'success')
        return redirect(url_for('wahana_bp.wahana_list'))
    except Exception as e:
        return handle_mysql_error(e, 'wahana_bp.wahana_edit')

def delete_wahana(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM wahana WHERE id_wahana=%s", (id,))
        mysql.connection.commit()
        cur.close()
        flash('Wahana berhasil dihapus!', 'info')
        return redirect(url_for('wahana_bp.wahana_list'))
    except Exception as e:
        return handle_mysql_error(e, 'wahana_bp.wahana_list')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}
