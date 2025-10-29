from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.utils.helpers import login_required, role_required
from app import mysql
from app.utils.error_handler import handle_mysql_error

# Blueprint specifically for admin validasi management
validasi_admin_bp = Blueprint('validasi_admin_bp', __name__)

# -----------------------------
# 🧾 LIST VALIDASI
# -----------------------------
@validasi_admin_bp.route('/admin/validasi')
@login_required
@role_required('admin')
def validasi_admin():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                v.id_validasi,
                p.nama_pengguna,
                w.nama_wahana,
                v.waktu_validasi
            FROM validasi v
            JOIN pengguna p ON v.id_pengguna = p.id_pengguna
            JOIN wahana w ON v.id_wahana = w.id_wahana
            ORDER BY v.waktu_validasi DESC
        """)
        validasi = cur.fetchall()
        cur.close()
    except Exception as e:
        return handle_mysql_error(e, 'validasi_admin_bp.validasi_admin')

    return render_template('admin/validasi_admin.html', validasi=validasi)


# -----------------------------
# ➕ TAMBAH VALIDASI
# -----------------------------
@validasi_admin_bp.route('/admin/validasi/tambah', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def tambah_validasi():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_pengguna, nama_pengguna FROM pengguna WHERE peran = 'staff'")
    staff_list = cur.fetchall()

    cur.execute("SELECT id_wahana, nama_wahana FROM wahana")
    wahana_list = cur.fetchall()
    cur.close()

    if request.method == 'POST':
        id_pengguna = request.form['id_pengguna']
        id_wahana = request.form['id_wahana']

        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO validasi (id_pengguna, id_wahana)
                VALUES (%s, %s)
            """, (id_pengguna, id_wahana))
            mysql.connection.commit()
            cur.close()
            flash('Validasi berhasil ditambahkan!', 'success')
            return redirect(url_for('validasi_admin_bp.validasi_admin'))
        except Exception as e:
            return handle_mysql_error(e, 'validasi_admin_bp.tambah_validasi')

    return render_template('admin/validasi_tambah.html', staff_list=staff_list, wahana_list=wahana_list)


# -----------------------------
# ✏️ EDIT VALIDASI
# -----------------------------
@validasi_admin_bp.route('/admin/validasi/edit/<int:id_validasi>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_validasi(id_validasi):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id_validasi, id_pengguna, id_wahana 
        FROM validasi WHERE id_validasi = %s
    """, (id_validasi,))
    validasi = cur.fetchone()

    cur.execute("SELECT id_pengguna, nama_pengguna FROM pengguna WHERE peran = 'staff'")
    staff_list = cur.fetchall()

    cur.execute("SELECT id_wahana, nama_wahana FROM wahana")
    wahana_list = cur.fetchall()
    cur.close()

    if request.method == 'POST':
        id_pengguna = request.form['id_pengguna']
        id_wahana = request.form['id_wahana']

        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE validasi 
                SET id_pengguna = %s, id_wahana = %s
                WHERE id_validasi = %s
            """, (id_pengguna, id_wahana, id_validasi))
            mysql.connection.commit()
            cur.close()
            flash('Data validasi berhasil diperbarui!', 'success')
            return redirect(url_for('validasi_admin_bp.validasi_admin'))
        except Exception as e:
            return handle_mysql_error(e, 'validasi_admin_bp.edit_validasi')

    return render_template('admin/validasi_edit.html', validasi=validasi, staff_list=staff_list, wahana_list=wahana_list)


# -----------------------------
# 🗑️ HAPUS VALIDASI
# -----------------------------
@validasi_admin_bp.route('/admin/validasi/hapus/<int:id_validasi>')
@login_required
@role_required('admin')
def hapus_validasi(id_validasi):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM validasi WHERE id_validasi = %s", (id_validasi,))
        mysql.connection.commit()
        cur.close()
        flash('Data validasi berhasil dihapus!', 'success')
    except Exception as e:
        return handle_mysql_error(e, 'validasi_admin_bp.hapus_validasi')

    return redirect(url_for('validasi_admin_bp.validasi_admin'))
