from flask import Blueprint, render_template, request, session, jsonify, flash, redirect, url_for
from datetime import datetime, timedelta
from app import mysql
from app.models.reservasi_model import get_reservasi, add_reservasi
from app.models.sesi_model import get_sesi
from app.utils.helpers import login_required, role_required

reservasi_bp = Blueprint('reservasi_bp', __name__)

# ============================
# 🧾 User Reservation List
# ============================
@reservasi_bp.route('/reservasi')
@login_required
@role_required('pelanggan', 'admin')
def reservasi_list():
    data = get_reservasi(session)
    return render_template('reservasi/reservasi_list.html', reservasi=data)


# ============================
# 🆕 User Add Reservation (Calendar Flow)
# ============================
@reservasi_bp.route('/reservasi/add', methods=['GET', 'POST'])
@login_required
@role_required('pelanggan')
def reservasi_add():
    if request.method == 'POST':
        return add_reservasi(request.form, session)

    # Render calendar-style form
    return render_template(
        'reservasi/reservasi_add.html',
        now=datetime.now(),
        timedelta=timedelta
    )


# ============================
# 📡 API: Get All Active Wahana
# ============================
@reservasi_bp.route('/api/wahana')
@login_required
@role_required('pelanggan')
def api_wahana():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_wahana, nama_wahana FROM wahana WHERE status_wahana = 'aktif'")
    data = cur.fetchall()
    cur.close()
    return jsonify(data)


# ============================
# 📡 API: Get Sessions by Wahana + Date
# ============================
@reservasi_bp.route('/api/sesi/<int:id_wahana>/<string:selected_date>')
@login_required
@role_required('pelanggan')
def api_sesi_by_date(id_wahana, selected_date):
    """
    Returns all sessions for a specific wahana and date.
    Example: /api/sesi/3/2025-11-14
    """
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT s.id_sesi, s.nama_sesi, s.kuota, s.harga, s.waktu_mulai, s.waktu_selesai
            FROM sesi s
            WHERE s.id_wahana = %s
              AND DATE(s.waktu_mulai) = %s
              AND s.kuota > 0
            ORDER BY s.waktu_mulai
        """, (id_wahana, selected_date))
        data = cur.fetchall()
        cur.close()
        return jsonify(data)
    except Exception as e:
        print("API Error:", e)
        return jsonify({"error": str(e)}), 500


# ============================
# ⚙️ (Optional) Admin View All Reservations
# ============================
@reservasi_bp.route('/reservasi/admin')
@login_required
@role_required('admin')
def reservasi_admin():
    data = get_reservasi(session)
    return render_template('reservasi/reservasi_admin.html', reservasi=data)
