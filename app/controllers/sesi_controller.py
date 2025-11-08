from flask import Blueprint, render_template, request, url_for, redirect, flash
from app.models.sesi_model import get_sesi_grouped, get_sesi_paginated, add_sesi, edit_sesi, delete_sesi
from app.utils.helpers import login_required, role_required
from app.models.wahana_model import get_wahana

sesi_bp = Blueprint('sesi_bp', __name__)

@sesi_bp.route('/sesi')
@login_required
@role_required('admin')
def sesi_list():
    wahana_filter = request.args.get('wahana')
    month_filter = request.args.get('month')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    # Pass filters into your data fetch function
    rows, total = get_sesi_paginated(
        page=page, per_page=per_page,
        wahana_filter=wahana_filter,
        month_filter=month_filter
    )

    # Group rows
    grouped_sesi = {}
    for row in rows:
        wahana_name = row[6]
        date = row[4].date() if row[4] else None
        if not date:
            continue
        month_key = date.strftime("%Y-%m")
        day_key = date.strftime("%Y-%m-%d")
        grouped_sesi.setdefault(wahana_name, {}).setdefault(month_key, {}).setdefault(day_key, []).append(row)

    # Get global wahana/month lists for dropdowns
    full_grouped = get_sesi_grouped()
    all_wahana = list(full_grouped.keys())
    all_months = sorted({month for wahana in full_grouped.values() for month in wahana.keys()})

    return render_template(
        'sesi/sesi_list.html',
        grouped_sesi=grouped_sesi,
        all_wahana=all_wahana,
        all_months=all_months,
        current_wahana=wahana_filter,
        current_month=month_filter,
        page=page,
        per_page=per_page,
        total=total
    )


# -------------------- ADD / EDIT / DELETE --------------------
# @sesi_bp.route('/sesi/add', methods=['GET', 'POST'])
# @login_required
# @role_required('admin')
# def sesi_add():
#     if request.method == 'POST':
#         add_sesi(request.form)
#         flash('✅ Sesi berhasil ditambahkan!', 'success')
#         return redirect(url_for('sesi_bp.sesi_list'))
#     return render_template('sesi/sesi_form.html')

@sesi_bp.route('/sesi/wahana/<int:id_wahana>')
@login_required
@role_required('admin')
def sesi_list_by_wahana(id_wahana):
    from app.models.sesi_model import get_sesi_by_wahana
    from app.models.wahana_model import get_wahana
    sesi_list = get_sesi_by_wahana(id_wahana)
    wahana = get_wahana(id=id_wahana)
    nama_wahana = wahana[1] if wahana else 'Tidak ditemukan'
    return render_template(
        'sesi/sesi_list.html',
        sesi_list=sesi_list,
        id_wahana=id_wahana,
        nama_wahana=nama_wahana
    )

@sesi_bp.route('/sesi/add/<int:id_wahana>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def sesi_add(id_wahana):
    wahana = get_wahana(id=id_wahana)
    nama_wahana = wahana[1] if wahana else ''
    if request.method == 'POST':
        nama_sesi = (request.form.get('nama_sesi') or '').strip()
        kuota = request.form.get('kuota')
        harga = request.form.get('harga')
        waktu_mulai = request.form.get('waktu_mulai')
        waktu_selesai = request.form.get('waktu_selesai')
        error = None

        if not nama_sesi or not kuota or not harga or not waktu_mulai or not waktu_selesai:
            error = 'Semua field wajib diisi!'
        else:
            try:
                kuota_int = int(kuota)
                harga_int = int(harga)
                if kuota_int <= 0:
                    error = 'Kuota harus lebih besar dari 0.'
                if harga_int < 0:
                    error = 'Harga tidak boleh negatif.'
            except ValueError:
                error = 'Kuota dan harga harus berupa angka.'

        if error:
            flash(error, 'danger')
            return render_template('sesi/sesi_form.html', id_wahana=id_wahana, nama_wahana=nama_wahana)

        add_sesi(request.form)
        flash('✅ Sesi berhasil ditambahkan!', 'success')
        return redirect(url_for('sesi_bp.sesi_list_by_wahana', id_wahana=id_wahana))
    return render_template('sesi/sesi_form.html', id_wahana=id_wahana, nama_wahana=nama_wahana)

@sesi_bp.route('/sesi/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def sesi_edit(id):
    from app.models.sesi_model import get_sesi, edit_sesi
    sesi = get_sesi(id=id)
    id_wahana = sesi[1] if sesi else None
    wahana = get_wahana(id=id_wahana)
    nama_wahana = wahana[1] if wahana else ''
    if request.method == 'POST':
        # Validasi input di controller
        nama_sesi = (request.form.get('nama_sesi') or '').strip()
        kuota = request.form.get('kuota')
        harga = request.form.get('harga')
        waktu_mulai = request.form.get('waktu_mulai')
        waktu_selesai = request.form.get('waktu_selesai')
        error = None

        if not nama_sesi or not kuota or not harga or not waktu_mulai or not waktu_selesai:
            error = 'Semua field wajib diisi!'
        else:
            try:
                kuota_int = int(kuota)
                harga_int = int(harga)
                if kuota_int <= 0:
                    error = 'Kuota harus lebih besar dari 0.'
                if harga_int < 0:
                    error = 'Harga tidak boleh negatif.'
            except ValueError:
                error = 'Kuota dan harga harus berupa angka.'

        if error:
            flash(error, 'danger')
            return render_template('sesi/sesi_form.html', sesi=sesi, id_wahana=id_wahana, nama_wahana=nama_wahana)

        edit_sesi(id, request.form)
        flash('✅ Sesi berhasil diperbarui!', 'success')
        return redirect(url_for('sesi_bp.sesi_list_by_wahana', id_wahana=id_wahana))

    return render_template('sesi/sesi_form.html', sesi=sesi, id_wahana=id_wahana, nama_wahana=nama_wahana)


@sesi_bp.route('/sesi/delete/<int:id>')
@login_required
@role_required('admin')
def sesi_delete(id):
    from app.models.sesi_model import get_sesi
    sesi = get_sesi(id=id)
    id_wahana = sesi[1] if sesi else None
    delete_sesi(id)
    flash('🗑️ Sesi dihapus!', 'info')
    return redirect(url_for('sesi_bp.sesi_list_by_wahana', id_wahana=id_wahana))