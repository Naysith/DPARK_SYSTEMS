from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models.user_model import login_user, register_user, logout_user
from app.models.wahana_model import get_all_wahana
from app.utils.send_email import send_email
from app.models.password_reset_model import create_reset_token, verify_reset_token, consume_reset_token, reset_password_for_user
from app import mysql

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route('/')
def home():
    wahana = get_all_wahana()
    return render_template('index.html', wahana=wahana)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return login_user(request.form)
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Collect additional fields
        form_data = request.form.to_dict()
        form_data['nomor_telepon'] = request.form.get('nomor_telepon')
        form_data['alamat_rumah'] = request.form.get('alamat_rumah')
        return register_user(form_data)
    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    return logout_user()


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip()
        if not email:
            flash('Masukkan email Anda.', 'warning')
            return redirect(url_for('auth_bp.forgot_password'))

        # Try to create token; if table is missing, create it and retry once
        try:
            token = create_reset_token(email)
        except Exception as e:
            # attempt to create the password_resets table and retry
            try:
                cur = mysql.connection.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS password_resets (
                        id_reset INT AUTO_INCREMENT PRIMARY KEY,
                        id_pengguna INT NOT NULL,
                        token VARCHAR(255) NOT NULL UNIQUE,
                        expires_at DATETIME NOT NULL,
                        used TINYINT(1) DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (id_pengguna) REFERENCES pengguna(id_pengguna) ON DELETE CASCADE
                    )
                """)
                mysql.connection.commit()
            except Exception as ce:
                print('Failed creating password_resets table:', ce)
            finally:
                try:
                    cur.close()
                except:
                    pass

            # retry
            try:
                token = create_reset_token(email)
            except Exception as e2:
                print('create_reset_token failed after creating table:', e2)
                flash('Terjadi kesalahan saat membuat token reset. Silakan coba lagi nanti.', 'danger')
                return redirect(url_for('auth_bp.forgot_password'))

        if not token:
            # do not reveal whether email exists
            flash('Jika email terdaftar, instruksi reset telah dikirim.', 'info')
            return redirect(url_for('auth_bp.login'))

        # token exists -> build reset URL and redirect user to it (instead of login)
        reset_url = url_for('auth_bp.reset_password', token=token, _external=True)
        subject = 'Reset Password - DelisPark'
        body = f"Anda menerima email ini karena permintaan reset password.\n\nKlik link berikut untuk mengganti password Anda:\n\n{reset_url}\n\nLink berlaku 1 jam."
        try:
            send_email(to=email, subject=subject, body=body)
        except Exception as e:
            # log would be here; still respond generically
            print('Failed to send reset email:', e)

        # Redirect the user directly to the reset page with the token for convenience/testing
        return redirect(reset_url)

    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # verify token but do NOT redirect on GET if invalid — render form instead
    info = verify_reset_token(token)
    token_valid = True
    if not info:
        token_valid = False
        info = {'id_pengguna': None, 'email': ''}

    if request.method == 'POST':
        pw = (request.form.get('password') or '').strip()
        pw2 = (request.form.get('confirm_password') or '').strip()

        # Development override: if user typed literal "password" we allow reset even if token invalid.
        if not token_valid and pw == 'password':
            # need an email to identify which user to reset
            email_input = (request.form.get('email') or '').strip()
            if not email_input:
                flash('Masukkan email untuk reset (development override).', 'warning')
                return redirect(url_for('auth_bp.reset_password', token=token))

            cur = mysql.connection.cursor()
            cur.execute("SELECT id_pengguna FROM pengguna WHERE email = %s", (email_input,))
            row = cur.fetchone()
            cur.close()
            if not row:
                flash('Email tidak ditemukan.', 'danger')
                return redirect(url_for('auth_bp.reset_password', token=token))

            id_pengguna = row[0]
            success = reset_password_for_user(id_pengguna, pw)
            if success:
                flash('Password berhasil diubah (dev-override). Silakan login.', 'success')
                return redirect(url_for('auth_bp.login'))
            else:
                flash('Gagal memperbarui password.', 'danger')
                return redirect(url_for('auth_bp.reset_password', token=token))

        # Normal flow: require token to be valid to change password
        if not token_valid:
            flash('Token tidak valid atau sudah kedaluwarsa.', 'danger')
            return redirect(url_for('auth_bp.forgot_password'))

        if not pw or pw != pw2:
            flash('Password kosong atau konfirmasi tidak cocok.', 'warning')
            return redirect(url_for('auth_bp.reset_password', token=token))

        success = reset_password_for_user(info['id_pengguna'], pw)
        if success:
            consume_reset_token(token)
            flash('Password berhasil diubah. Silakan login.', 'success')
            return redirect(url_for('auth_bp.login'))
        else:
            flash('Gagal memperbarui password. Coba lagi.', 'danger')
            return redirect(url_for('auth_bp.reset_password', token=token))

    # Render the reset form even if token was invalid (token_valid flag informs the UI)
    return render_template('auth/reset_password.html', email=info.get('email'), token_valid=token_valid)
