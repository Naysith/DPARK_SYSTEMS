from functools import wraps
from flask import session, flash, redirect, url_for

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'id_pengguna' not in session:
            flash('Silakan login terlebih dahulu.')
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return wrapper

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'peran' not in session or session['peran'] not in roles:
                flash('Akses ditolak.')
                return redirect(url_for('auth_bp.home'))
            return f(*args, **kwargs)
        return wrapper
    return decorator
