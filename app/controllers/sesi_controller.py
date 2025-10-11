from flask import Blueprint, render_template, request
from app.utils.helpers import login_required, role_required
from app.models.sesi_model import get_sesi, add_sesi, edit_sesi, delete_sesi
from app import mysql

sesi_bp = Blueprint('sesi_bp', __name__)

# ---------------- LIST ----------------
@sesi_bp.route('/sesi')
@login_required
@role_required('admin')
def sesi_list():
    sesi = get_sesi()
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_wahana, nama_wahana FROM wahana")
    wahana = cur.fetchall()
    cur.close()
    return render_template('sesi/sesi_list.html', sesi=sesi, wahana=wahana)

# ---------------- ADD ----------------
@sesi_bp.route('/sesi/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def sesi_add():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_wahana, nama_wahana FROM wahana")
    wahana = cur.fetchall()
    cur.close()

    if request.method == 'POST':
        return add_sesi(request.form)
    return render_template('sesi/sesi_form.html', wahana=wahana)

# ---------------- EDIT ----------------
@sesi_bp.route('/sesi/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def sesi_edit(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_wahana, nama_wahana FROM wahana")
    wahana = cur.fetchall()
    cur.close()

    if request.method == 'POST':
        return edit_sesi(id, request.form)
    sesi = get_sesi(id)
    return render_template('sesi/sesi_form.html', sesi=sesi, wahana=wahana)

# ---------------- DELETE ----------------
@sesi_bp.route('/sesi/delete/<int:id>')
@login_required
@role_required('admin')
def sesi_delete(id):
    return delete_sesi(id)
