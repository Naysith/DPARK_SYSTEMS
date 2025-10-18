from flask import Blueprint, render_template, request, url_for, redirect, flash
from app.models.sesi_model import get_sesi_grouped, get_sesi_paginated, add_sesi, edit_sesi, delete_sesi
from app.utils.helpers import login_required, role_required

sesi_bp = Blueprint('sesi_bp', __name__)

@sesi_bp.route('/sesi')
@login_required
@role_required('admin')
def sesi_list():
    # pagination
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    rows, total = get_sesi_paginated(page=page, per_page=per_page)

    # Group only the paginated rows
    grouped_sesi = {}
    for row in rows:
        wahana_name = row[6]
        date = row[4].date() if row[4] else None
        if not date:
            continue
        month_key = date.strftime("%Y-%m")
        day_key = date.strftime("%Y-%m-%d")
        grouped_sesi.setdefault(wahana_name, {})
        grouped_sesi[wahana_name].setdefault(month_key, {})
        grouped_sesi[wahana_name][month_key].setdefault(day_key, []).append(row)

    wahana_filter = request.args.get('wahana')
    month_filter = request.args.get('month')

    # Filter by wahana
    if wahana_filter and wahana_filter in grouped_sesi:
        grouped_sesi = {wahana_filter: grouped_sesi[wahana_filter]}

    # Extract all months from all wahana (using full dataset)
    all_months = sorted({
        month for wahana in get_sesi_grouped().values() for month in wahana.keys()
    })

    # Filter by selected month
    if month_filter:
        for w, months in grouped_sesi.items():
            grouped_sesi[w] = {
                m: d for m, d in months.items() if m == month_filter
            }

    return render_template(
        'sesi/sesi_list.html',
        grouped_sesi=grouped_sesi,
        all_wahana=list(get_sesi_grouped().keys()),
        all_months=all_months,
        current_wahana=wahana_filter,
        current_month=month_filter,
        page=page,
        per_page=per_page,
        total=total
    )


# -------------------- ADD / EDIT / DELETE --------------------
@sesi_bp.route('/sesi/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def sesi_add():
    if request.method == 'POST':
        add_sesi(request.form)
        flash('✅ Sesi berhasil ditambahkan!', 'success')
        return redirect(url_for('sesi_bp.sesi_list'))
    return render_template('sesi/sesi_form.html')


@sesi_bp.route('/sesi/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def sesi_edit(id):
    if request.method == 'POST':
        edit_sesi(id, request.form)
        flash('✅ Sesi berhasil diperbarui!', 'success')
        return redirect(url_for('sesi_bp.sesi_list'))
    from app.models.sesi_model import get_sesi
    sesi = get_sesi(id=id)
    return render_template('sesi/sesi_form.html', sesi=sesi)


@sesi_bp.route('/sesi/delete/<int:id>')
@login_required
@role_required('admin')
def sesi_delete(id):
    delete_sesi(id)
    flash('🗑️ Sesi dihapus!', 'info')
    return redirect(url_for('sesi_bp.sesi_list'))