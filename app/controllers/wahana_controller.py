from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.wahana_model import get_wahana, add_wahana, edit_wahana, delete_wahana
from flask import send_file, abort, Response
from app.utils.helpers import login_required, role_required
from app.utils.error_handler import handle_mysql_error

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
