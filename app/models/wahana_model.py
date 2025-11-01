from app import mysql
from werkzeug.utils import secure_filename
from uuid import uuid4
import os
from flask import flash, redirect, url_for
from app.utils.error_handler import handle_mysql_error
from MySQLdb.cursors import DictCursor

UPLOAD_FOLDER = 'app/static/uploads'

# ---------------- GET WAHANA ----------------
def get_wahana(id=None):
    try:
        cur = mysql.connection.cursor()
        if id:
            cur.execute("SELECT * FROM wahana WHERE id_wahana=%s", (id,))
            data = cur.fetchone()
        else:
            cur.execute("SELECT * FROM wahana")
            data = cur.fetchall()
        cur.close()
        # Return raw DB rows; image column may be bytes (LONGBLOB) or filename string.
        return data
    except Exception as e:
        return handle_mysql_error(e, 'wahana_bp.wahana_list')


# ---------------- ADD WAHANA ----------------
def add_wahana(form, files):
    try:
        nama = form['nama_wahana'].strip()
        deskripsi = form['deskripsi']
        status = form['status_wahana']
        gambar = files.get('gambar_wahana')
        filename = None

        # ✅ Duplicate check
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM wahana WHERE LOWER(nama_wahana) = LOWER(%s)", (nama,))
        exists = cur.fetchone()[0]
        if exists:
            flash("❌ Nama wahana sudah ada!", "danger")
            cur.close()
            return redirect(url_for('wahana_bp.wahana_add'))

        # Save image bytes into LONGBLOB column if valid
        image_bytes = None
        if gambar and allowed_file(gambar.filename):
            image_bytes = gambar.read()

        # Insert new wahana (gambar_wahana stores bytes or NULL)
        cur.execute("""
            INSERT INTO wahana (nama_wahana, deskripsi, status_wahana, gambar_wahana)
            VALUES (%s, %s, %s, %s)
        """, (nama, deskripsi, status, image_bytes))
        mysql.connection.commit()
        cur.close()
        flash('✅ Wahana berhasil ditambahkan!', 'success')
        return redirect(url_for('wahana_bp.wahana_list'))
    except Exception as e:
        return handle_mysql_error(e, 'wahana_bp.wahana_add')


# ---------------- EDIT WAHANA ----------------
def edit_wahana(id, form, files):
    try:
        nama = form['nama_wahana'].strip()
        deskripsi = form['deskripsi']
        status = form['status_wahana']
        gambar = files.get('gambar_wahana')
        filename = None

        cur = mysql.connection.cursor()

        # ✅ Duplicate check (exclude current wahana)
        cur.execute("""
            SELECT COUNT(*) FROM wahana 
            WHERE LOWER(nama_wahana) = LOWER(%s) AND id_wahana != %s
        """, (nama, id))
        exists = cur.fetchone()[0]
        if exists:
            flash("❌ Nama wahana sudah digunakan oleh wahana lain!", "danger")
            cur.close()
            return redirect(url_for('wahana_bp.wahana_edit', id=id))

        # Read new image bytes if uploaded
        image_bytes = None
        if gambar and allowed_file(gambar.filename):
            image_bytes = gambar.read()

        # Update data: if new image bytes provided, update blob column; otherwise keep existing
        if image_bytes is not None:
            cur.execute("""
                UPDATE wahana 
                SET nama_wahana=%s, deskripsi=%s, status_wahana=%s, gambar_wahana=%s
                WHERE id_wahana=%s
            """, (nama, deskripsi, status, image_bytes, id))
        else:
            cur.execute("""
                UPDATE wahana 
                SET nama_wahana=%s, deskripsi=%s, status_wahana=%s
                WHERE id_wahana=%s
            """, (nama, deskripsi, status, id))
        mysql.connection.commit()
        cur.close()
        flash('✅ Wahana berhasil diperbarui!', 'success')
        return redirect(url_for('wahana_bp.wahana_list'))
    except Exception as e:
        return handle_mysql_error(e, 'wahana_bp.wahana_edit')


# ---------------- DELETE WAHANA ----------------
def delete_wahana(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM wahana WHERE id_wahana=%s", (id,))
        mysql.connection.commit()
        cur.close()
        flash('🗑️ Wahana berhasil dihapus!', 'info')
        return redirect(url_for('wahana_bp.wahana_list'))
    except Exception as e:
        return handle_mysql_error(e, 'wahana_bp.wahana_list')


# ---------------- GETALL WAHANA ----------------
def get_all_wahana():
    from app import mysql
    cur = mysql.connection.cursor()
    # Query HANYA menggunakan kolom yang ADA di database
    cur.execute("SELECT id_wahana, nama_wahana, deskripsi, status_wahana, gambar_wahana FROM wahana") 
    wahana = cur.fetchall()
    cur.close()
    return wahana

# ---------------- FILE VALIDATION ----------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}
