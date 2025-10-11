from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.wahana_model import get_wahana, add_wahana, edit_wahana, delete_wahana
from app.utils.helpers import login_required, role_required

# Blueprint setup
wahana_bp = Blueprint('wahana_bp', __name__)

# ===============================
# List Wahana
# ===============================
@wahana_bp.route('/wahana')
@login_required
@role_required('admin')
def wahana_list():
    """
    Display all available wahana for admin management.
    """
    wahana = get_wahana()
    return render_template('wahana/wahana_list.html', wahana=wahana)


# ===============================
# Add Wahana
# ===============================
@wahana_bp.route('/wahana/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def wahana_add():
    """
    Add a new wahana (ride/attraction).
    """
    if request.method == 'POST':
        add_wahana(request.form, request.files)
        flash('✅ Wahana berhasil ditambahkan!', 'success')
        return redirect(url_for('wahana_bp.wahana_list'))

    return render_template('wahana/wahana_form.html')


# ===============================
# Edit Wahana
# ===============================
@wahana_bp.route('/wahana/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def wahana_edit(id):
    """
    Edit an existing wahana.
    """
    if request.method == 'POST':
        edit_wahana(id, request.form, request.files)
        flash('✅ Wahana berhasil diperbarui!', 'success')
        return redirect(url_for('wahana_bp.wahana_list'))

    wahana = get_wahana(id)
    return render_template('wahana/wahana_form.html', wahana=wahana)


# ===============================
# Delete Wahana
# ===============================
@wahana_bp.route('/wahana/delete/<int:id>')
@login_required
@role_required('admin')
def wahana_delete(id):
    """
    Delete a wahana by ID.
    """
    delete_wahana(id)
    flash('🗑️ Wahana berhasil dihapus!', 'info')
    return redirect(url_for('wahana_bp.wahana_list'))
