from flask import Blueprint, render_template, request
from app.utils.helpers import login_required, role_required
from app.models.user_model import get_users, add_user, edit_user, delete_user

user_bp = Blueprint('user_bp', __name__)

# ---------------- USERS LIST ----------------
@user_bp.route('/users')
@login_required
@role_required('admin')
def users_list():
    users = get_users()
    return render_template('users/list.html', users=users)

# ---------------- ADD USER ----------------
@user_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def users_add():
    if request.method == 'POST':
        return add_user(request.form)
    return render_template('users/form.html')

# ---------------- EDIT USER ----------------
@user_bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def users_edit(id):
    if request.method == 'POST':
        return edit_user(id, request.form)
    user = get_users(id)
    return render_template('users/form.html', user=user)

# ---------------- DELETE USER ----------------
@user_bp.route('/users/delete/<int:id>')
@login_required
@role_required('admin')
def users_delete(id):
    return delete_user(id)
