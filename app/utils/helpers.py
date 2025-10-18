from functools import wraps
from flask import session, flash, redirect, url_for, current_app

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
            # Log minimal session info for debugging (avoid dumping full session)
            current_app.logger.debug(f"session id={session.get('id_pengguna')} peran={session.get('peran')}")
            if 'peran' not in session or session['peran'] not in roles:
                flash(f"Akses ditolak. Role Anda: {session.get('peran')}")
                return redirect(url_for('auth_bp.login'))
            return f(*args, **kwargs)
        return wrapper
    return decorator

def parse_datetime_local(value):
    """
    Converts HTML datetime-local input (YYYY-MM-DDTHH:MM)
    into a format compatible with MySQL (YYYY-MM-DD HH:MM:SS)
    """
    if not value:
        return None
    v = value.replace('T', ' ')
    if len(v) == 16:
        v += ":00"  # ensure seconds
    return v
