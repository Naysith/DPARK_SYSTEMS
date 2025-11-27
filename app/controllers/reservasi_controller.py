import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.controllers.sesi_controller import sesi_list
from app.models import reservasi_model, pembayaran_model
from app.models import wahana_model, sesi_model
from app.utils.helpers import login_required, role_required
from app.utils.error_handler import handle_mysql_error

reservasi_bp = Blueprint('reservasi_bp', __name__)

# --- List all reservations for the logged-in user ---
@reservasi_bp.route('/reservasi/list')
@login_required
@role_required('pelanggan')
def reservasi_list():
    try:
        id_pengguna = session.get('id_pengguna')
        reservasi = reservasi_model.get_reservasi_by_user(id_pengguna)
        return render_template('reservasi/reservasi_list.html', reservasi=reservasi)
    except Exception as e:
        return handle_mysql_error(e, 'user_bp.user_dashboard')


# --- New user-friendly reservation flow ---
@reservasi_bp.route('/reservasi/start')
@login_required
@role_required('pelanggan')
def reservasi_start():
    try:
        wahana = wahana_model.get_all_wahana()
        return render_template('reservasi/select_wahana.html', wahana_list=wahana)
    except Exception as e:
        return handle_mysql_error(e, 'user_bp.user_dashboard')


@reservasi_bp.route('/reservasi/select_date/<int:id_wahana>', methods=['GET'])
@login_required
@role_required('pelanggan')
def reservasi_select_date(id_wahana):
    try:
        # show next 14 days for user to pick
        from datetime import date, timedelta
        days = [(date.today() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(0, 14)]
        # pass id_wahana for the template to use when posting
        return render_template('reservasi/select_date.html', days=days, id_wahana=id_wahana)
    except Exception as e:
        return handle_mysql_error(e, 'user_bp.user_dashboard')


@reservasi_bp.route('/reservasi/select_session', methods=['POST'])
@login_required
@role_required('pelanggan')
def reservasi_select_session():
    try:
        id_wahana = int(request.form['id_wahana'])
        date_chosen = request.form['date']  # YYYY-MM-DD
        period = request.form.get('period')  # 'pagi'|'siang'|'malam'

        sesi = sesi_model.find_sesi_for_date_and_period(id_wahana, date_chosen, period)
        if not sesi:
            flash('Maaf, tidak ada sesi tersedia untuk pilihan ini. Silakan pilih tanggal/waktu lain.', 'warning')
            return redirect(url_for('reservasi_bp.reservasi_select_date', id_wahana=id_wahana))

        # sesi is a row tuple: id_sesi, nama_sesi, kuota, harga, waktu_mulai, waktu_selesai, nama_wahana
        return render_template('reservasi/select_session.html', sesi=sesi, date=date_chosen, id_wahana=id_wahana)
    except Exception as e:
        return handle_mysql_error(e, 'user_bp.user_dashboard')


@reservasi_bp.route('/reservasi/confirm', methods=['POST'])
@login_required
@role_required('pelanggan')
def reservasi_confirm():
    try:
        id_pengguna = session.get('id_pengguna')
        id_sesi = int(request.form['id_sesi'])
        jumlah_tiket = int(request.form.get('jumlah_tiket', 1))

        new_id = reservasi_model.add_reservasi_return_id(id_pengguna, id_sesi, jumlah_tiket)
        if not new_id:
            flash('Gagal membuat reservasi. Silakan coba lagi.', 'danger')
            return redirect(url_for('reservasi_bp.reservasi_start'))

        return redirect(url_for('reservasi_bp.pembayaran_form', id_reservasi=new_id))
    except Exception as e:
        return handle_mysql_error(e, 'user_bp.user_dashboard')

# --- Add new reservation ---
@reservasi_bp.route('/reservasi/add', methods=['GET', 'POST'], endpoint='reservasi_add')
@login_required
@role_required('pelanggan')
def reservasi_add_route():
    try:
        id_wahana = request.args.get('id_wahana', type=int)
        wahana_list = wahana_model.get_all_wahana()
        now = datetime.datetime.now()
        if request.method == 'POST':
            id_pengguna = session.get('id_pengguna')
            id_sesi = int(request.form['id_sesi'])
            jumlah_tiket = int(request.form['jumlah_tiket'])
            # Proses insert reservasi
            new_id = reservasi_model.add_reservasi_return_id(id_pengguna, id_sesi, jumlah_tiket)
            if not new_id:
                flash('Gagal membuat reservasi. Silakan coba lagi.', 'danger')
                return redirect(url_for('reservasi_bp.reservasi_add', id_wahana=id_wahana))
            return redirect(url_for('reservasi_bp.pembayaran_form', id_reservasi=new_id))
        return render_template(
            'reservasi/reservasi_add.html',
            sesi_list=sesi_list,
            wahana_list=wahana_list,
            now=now,
            timedelta=datetime.timedelta,
            id_wahana=id_wahana
        )
    except Exception as e:
        return handle_mysql_error(e, 'reservasi_bp.reservasi_list')



# --- API endpoints to support client-side reservation form ---
@reservasi_bp.route('/api/wahana')
def api_wahana_list():
    try:
        wahana = wahana_model.get_all_wahana()
        # Build a JSON-serializable list: [id, name, image_url, status]
        out = []
        for w in wahana:
            if isinstance(w, dict):
                wid = w.get('id_wahana') or w.get('id')
                name = w.get('nama_wahana') or ''
                status = w.get('status_wahana') or ''
            else:
                # tuple fallback (id, nama, deskripsi, status, gambar...)
                wid = w[0]
                name = w[1] if len(w) > 1 else ''
                status = w[3] if len(w) > 3 else ''
            try:
                img_url = url_for('wahana_bp.wahana_image', id=wid)
            except Exception:
                img_url = ''
            out.append([wid, name, img_url, status])
        return {'data': out}
    except Exception:
        return {'data': []}


@reservasi_bp.route('/api/sesi/<int:id_wahana>/<date_str>')
def api_sesi_for_date(id_wahana, date_str):
    try:
        # fetch all sessions on that date for the wahana
        cur = None
        from app import mysql
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT s.id_sesi, s.nama_sesi, s.kuota, s.harga, s.waktu_mulai, s.waktu_selesai
            FROM sesi s
            WHERE s.id_wahana=%s AND DATE(s.waktu_mulai)=%s AND s.kuota>0
            ORDER BY s.waktu_mulai
        """, (id_wahana, date_str))
        rows = cur.fetchall()
        cur.close()
        out = []
        for r in rows:
            # r may be tuple or dict-like depending on cursor; normalize
            if isinstance(r, dict):
                sid = r.get('id_sesi')
                nama = r.get('nama_sesi')
                kuota = r.get('kuota')
                harga = r.get('harga')
                mulai = r.get('waktu_mulai')
                selesai = r.get('waktu_selesai')
            else:
                sid = r[0]
                nama = r[1]
                kuota = r[2]
                harga = r[3]
                mulai = r[4]
                selesai = r[5]
            mulai_s = mulai.strftime('%Y-%m-%d %H:%M:%S') if hasattr(mulai, 'strftime') else str(mulai)
            selesai_s = selesai.strftime('%Y-%m-%d %H:%M:%S') if hasattr(selesai, 'strftime') else str(selesai)
            # return id, nama, kuota, harga, waktu_mulai_str, waktu_selesai_str
            out.append([sid, nama, int(kuota) if kuota is not None else 0, float(harga) if harga is not None else 0.0, mulai_s, selesai_s])
        return {'data': out}
    except Exception:
        if cur:
            cur.close()
        return {'data': []}

# --- Payment form and processing ---
@reservasi_bp.route('/pembayaran/<int:id_reservasi>', methods=['GET', 'POST'])
@login_required
@role_required('pelanggan')
def pembayaran_form(id_reservasi):
    try:
        if request.method == 'POST':
            result = pembayaran_model.add_pembayaran(id_reservasi, request.form)
            # result: {id_pembayaran, pdf_file, pdf_filepath, email_to, nama_user}
            if not result:
                flash('Gagal memproses pembayaran. Silakan coba lagi.', 'danger')
                return redirect(url_for('reservasi_bp.reservasi_list'))

            # Start background email send (non-blocking) if we have a filepath and recipient
            sending = False
            pdf_filepath = result.get('pdf_filepath')
            email_to = result.get('email_to')
            nama_user = result.get('nama_user')
            if pdf_filepath and email_to:
                try:
                    import threading
                    from app.utils.send_email import send_email

                    def _bg_send(path, to_addr):
                        try:
                            send_email(to=to_addr, subject='Your DelisPark Tickets', body='Thank you for your payment!', attachments=[path])
                            print(f"Background: email sent to {to_addr}")
                        except Exception as e:
                            print('Background email send failed:', e)

                    t = threading.Thread(target=_bg_send, args=(pdf_filepath, email_to), daemon=True)
                    t.start()
                    sending = True
                except Exception as e:
                    print('Failed to start background email thread:', e)

            # Render success page with e-ticket and sending indicator
            return render_template('pembayaran/success.html', pdf_file=result.get('pdf_file'), id_pembayaran=result.get('id_pembayaran'), email_to=email_to, sending=sending)

        reservasi = reservasi_model.get_reservasi(id_reservasi)
        return render_template('pembayaran/form.html', reservasi=reservasi)
    except Exception as e:
        return handle_mysql_error(e, 'reservasi_bp.reservasi_list')


@reservasi_bp.route('/pembayaran/send_email/<int:id_pembayaran>', methods=['POST'])
@login_required
@role_required('pelanggan')
def pembayaran_send_email(id_pembayaran):
    try:
        # Fetch payment -> reservation -> tickets -> user email
        from app import mysql
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT r.id_reservasi, u.email, u.nama_pengguna
            FROM pembayaran p
            JOIN reservasi r ON p.id_reservasi = r.id_reservasi
            JOIN pengguna u ON r.id_pengguna = u.id_pengguna
            WHERE p.id_pembayaran = %s
        """, (id_pembayaran,))
        row = cur.fetchone()
        if not row:
            flash('Pembayaran tidak ditemukan.', 'danger')
            cur.close()
            return redirect(url_for('reservasi_bp.reservasi_list'))
        id_reservasi = row[0]
        email_to = row[1]
        nama_user = row[2]

        # Fetch tickets
        cur.execute("""
            SELECT t.kode_tiket, w.nama_wahana, s.nama_sesi
            FROM tiket t
            JOIN sesi s ON t.id_sesi = s.id_sesi
            JOIN wahana w ON s.id_wahana = w.id_wahana
            WHERE t.id_reservasi = %s
        """, (id_reservasi,))
        tiket_list = cur.fetchall()

        # Generate PDF
        from app.utils.tiket_pdf import generate_ticket_pdf
        pdf_file = None
        pdf_filepath = None
        if tiket_list:
            # generate_ticket_pdf now returns (filepath, public_url)
            fp, public_url = generate_ticket_pdf(tiket_list, id_reservasi, nama_user)
            pdf_filepath = fp
            pdf_file = public_url

            # Send email
            from app.utils.send_email import send_email
            send_email(
                to=email_to,
                subject='Your DelisPark Tickets',
                body='Attached are your e-tickets.',
                attachments=[pdf_filepath]
            )

        cur.close()
        flash('Email dengan tiket telah dikirim.', 'success')
        return redirect(url_for('reservasi_bp.reservasi_list'))
    except Exception as e:
        return handle_mysql_error(e, 'reservasi_bp.reservasi_list')
