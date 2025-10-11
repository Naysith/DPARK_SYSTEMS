from flask import Blueprint, render_template, request, url_for, redirect, flash
from app.models.sesi_model import get_sesi_grouped, add_sesi, edit_sesi, delete_sesi
from app.utils.helpers import login_required, role_required

sesi_bp = Blueprint('sesi_bp', __name__)

@sesi_bp.route('/sesi')
@login_required
@role_required('admin')
def sesi_list():
    grouped_sesi = get_sesi_grouped()
    wahana_filter = request.args.get('wahana')
    month_filter = request.args.get('month')

    # Filter by wahana
    if wahana_filter and wahana_filter in grouped_sesi:
        grouped_sesi = {wahana_filter: grouped_sesi[wahana_filter]}

    # Extract all months from all wahana
    all_months = sorted({
        month for wahana in grouped_sesi.values() for month in wahana.keys()
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
        current_month=month_filter
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
