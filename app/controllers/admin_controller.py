from flask import Blueprint, render_template
from app.utils.helpers import login_required, role_required
from app.utils.sesi_auto import generate_auto_sesi

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@admin_bp.route('/admin/generate_sesi')
@role_required('admin')
def generate_sesi_auto():
    from app.utils.sesi_auto import generate_auto_sesi
    generate_auto_sesi()
    return "✅ Auto session generation complete! Check your sesi list."