from flask import Blueprint, render_template, request, jsonify
from app.utils.helpers import login_required, role_required
from app import mysql

staff_qr_bp = Blueprint('staff_qr_bp', __name__)

@staff_qr_bp.route('/staff/qr_scanner')
@login_required
@role_required('staff')
def qr_scanner():
    return render_template('staff/qr_scanner.html')

@staff_qr_bp.route('/staff/validate_qr')
@login_required
@role_required('staff')
def validate_qr():
    kode = request.args.get('code')
    cur = mysql.connection.cursor()
    cur.execute("SELECT status FROM reservasi WHERE kode_tiket = %s", (kode,))
    result = cur.fetchone()
    if result:
        if result[0] == 'belum_digunakan':
            cur.execute("UPDATE reservasi SET status='digunakan' WHERE kode_tiket=%s", (kode,))
            mysql.connection.commit()
            return jsonify({'valid': True, 'message': '✅ Tiket valid dan ditandai sebagai digunakan.'})
        else:
            return jsonify({'valid': False, 'message': '⚠️ Tiket sudah digunakan.'})
    else:
        return jsonify({'valid': False, 'message': '❌ Tiket tidak ditemukan.'})
