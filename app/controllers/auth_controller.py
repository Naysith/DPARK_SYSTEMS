from flask import Blueprint, render_template, request
from app.models.user_model import login_user, register_user, logout_user

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/')
def home():
    return render_template('index.html')

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
