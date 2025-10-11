from app import mysql
from werkzeug.utils import secure_filename
from uuid import uuid4
import os

UPLOAD_FOLDER = 'app/static/uploads'

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
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filename = secure_filename(f"{uuid4().hex}_{gambar.filename}")
        gambar.save(os.path.join(UPLOAD_FOLDER, filename))

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO wahana (nama_wahana, deskripsi, status_wahana, gambar_wahana)
        VALUES (%s, %s, %s, %s)
    """, (nama, deskripsi, status, filename))
    mysql.connection.commit()
    cur.close()

def edit_wahana(id, form, files):
    nama = form['nama_wahana']
    deskripsi = form['deskripsi']
    status = form['status_wahana']
    gambar = files.get('gambar_wahana')
    filename = None

    if gambar and allowed_file(gambar.filename):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filename = secure_filename(f"{uuid4().hex}_{gambar.filename}")
        gambar.save(os.path.join(UPLOAD_FOLDER, filename))

    cur = mysql.connection.cursor()
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

def delete_wahana(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM wahana WHERE id_wahana=%s", (id,))
    mysql.connection.commit()
    cur.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}
