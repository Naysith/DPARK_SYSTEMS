from flask import Blueprint, render_template
from app.utils.helpers import login_required, role_required

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')
