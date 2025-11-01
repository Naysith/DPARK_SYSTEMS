from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.wahana_model import get_wahana, add_wahana, edit_wahana, delete_wahana
from flask import send_file, abort, Response
from app.utils.helpers import login_required, role_required
from app.utils.error_handler import handle_mysql_error

wahana_bp = Blueprint('wahana_bp', __name__)

@wahana_bp.route('/wahana')
@login_required
@role_required('admin')
def wahana_list():
    try:
        wahana = get_wahana()
    except Exception as e:
        return handle_mysql_error(e, 'wahana_bp.wahana_list')
    return render_template('wahana/wahana_list.html', wahana=wahana)

@wahana_bp.route('/wahana/add', methods=['GET','POST'])
@login_required
@role_required('admin')
def wahana_add():
    if request.method == 'POST':
        try:
            add_wahana(request.form, request.files)
            flash('✅ Wahana berhasil ditambahkan!', 'success')
            return redirect(url_for('wahana_bp.wahana_list'))
        except Exception as e:
            return handle_mysql_error(e, 'wahana_bp.wahana_list')
    return render_template('wahana/wahana_form.html')

@wahana_bp.route('/wahana/edit/<int:id>', methods=['GET','POST'])
@login_required
@role_required('admin')
def wahana_edit(id):
    if request.method == 'POST':
        try:
            edit_wahana(id, request.form, request.files)
            flash('✅ Wahana berhasil diperbarui!', 'success')
            return redirect(url_for('wahana_bp.wahana_list'))
        except Exception as e:
            return handle_mysql_error(e, 'wahana_bp.wahana_list')
    try:
        wahana = get_wahana(id)
    except Exception as e:
        return handle_mysql_error(e, 'wahana_bp.wahana_list')
    return render_template('wahana/wahana_form.html', wahana=wahana)

@wahana_bp.route('/wahana/delete/<int:id>')
@login_required
@role_required('admin')
def wahana_delete(id):
    try:
        delete_wahana(id)
        flash('🗑️ Wahana berhasil dihapus!', 'info')
        return redirect(url_for('wahana_bp.wahana_list'))
    except Exception as e:
        return handle_mysql_error(e, 'wahana_bp.wahana_list')

@wahana_bp.route('/wahana/public')
def wahana_list_public():
    """
    Menampilkan daftar wahana untuk pengunjung umum. Tidak memerlukan login.
    """
    try:
        # Menggunakan fungsi model yang sama untuk mengambil data wahana
        wahana = get_wahana() 
    except Exception as e:
        # Menangani error database dengan pesan yang ramah
        flash('Terjadi kesalahan saat memuat daftar wahana. Coba lagi nanti.', 'danger')
        # Jika ada error, kirim ke homepage atau template yang sesuai
        return render_template('homepage.html') 
        
    return render_template('wahana/wahana_list_public.html', wahana=wahana)


# --- ROUTE IMAGE (Diperbarui untuk mendukung akses publik) ---

@wahana_bp.route('/wahana/image/<int:id>')
def wahana_image(id):
    """
    Menyajikan gambar wahana. Tidak perlu @login_required agar gambar bisa tampil 
    di wahana_list_public.html.
    """
    try:
        # Asumsi get_wahana(id) mengambil satu baris data wahana, 
        # di mana w[4] adalah data gambar (blob atau nama file).
        w = get_wahana(id) 
        if not w:
            abort(404)
        img = w[4]

        # Jika disimpan sebagai nama file (string), redirect ke static file
        if isinstance(img, str) and img:
            return redirect(url_for('static', filename='uploads/' + img))
        
        # Jika disimpan sebagai byte/blob, stream itu
        if isinstance(img, (bytes, bytearray)):
            # Coba menebak mimetype jika Anda menyimpannya di database
            # Jika tidak yakin, gunakan image/jpeg atau perlu menyimpan mimetype
            return Response(img, mimetype='image/jpeg') 
        
        # Gambar default jika tidak ada
        return redirect(url_for('static', filename='images/default_wahana.jpg')) 
        
    except Exception as e:
        # Jika terjadi error database atau lainnya
        return handle_mysql_error(e, 'wahana_bp.wahana_image')