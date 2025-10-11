from flask import Blueprint, render_template
from app.utils.helpers import login_required, role_required
from app.utils.sesi_auto import generate_auto_sesi
from app.utils.scheduler import get_scheduler_status
from flask import jsonify

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

@admin_bp.route('/admin/scheduler_status')
@role_required('admin')
def scheduler_status():
    """
    Render scheduler information in a styled HTML page.
    """
    status = get_scheduler_status()
    return render_template('scheduler_status.html', status=status)
