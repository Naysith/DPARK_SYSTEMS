from app import mysql
from uuid import uuid4
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

TOKEN_TTL_HOURS = 1

def create_reset_token(email):
    """Create a reset token for pengguna with given email. Returns token or None."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_pengguna FROM pengguna WHERE email = %s", (email,))
    row = cur.fetchone()
    if not row:
        cur.close()
        return None
    id_pengguna = row[0]
    token = uuid4().hex
    expires_at = datetime.utcnow() + timedelta(hours=TOKEN_TTL_HOURS)
    cur.execute("""
        INSERT INTO password_resets (id_pengguna, token, expires_at)
        VALUES (%s, %s, %s)
    """, (id_pengguna, token, expires_at.strftime('%Y-%m-%d %H:%M:%S')))
    mysql.connection.commit()
    cur.close()
    return token

def verify_reset_token(token):
    """Verify token: return dict with id_pengguna,email,nama_pengguna if valid, else None."""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT pr.id_pengguna, pr.expires_at, pr.used, p.email, p.nama_pengguna
        FROM password_resets pr
        JOIN pengguna p ON pr.id_pengguna = p.id_pengguna
        WHERE pr.token = %s
    """, (token,))
    row = cur.fetchone()
    if not row:
        cur.close()
        return None
    id_pengguna, expires_at, used, email, nama = row
    # expires_at may be returned as datetime or string; normalize
    try:
        if isinstance(expires_at, str):
            expires_at_dt = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')
        else:
            expires_at_dt = expires_at
    except Exception:
        expires_at_dt = None
    cur.close()
    if used:
        return None
    if not expires_at_dt or expires_at_dt < datetime.utcnow():
        return None
    return {'id_pengguna': id_pengguna, 'email': email, 'nama_pengguna': nama}

def consume_reset_token(token):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE password_resets SET used = 1 WHERE token = %s", (token,))
    mysql.connection.commit()
    cur.close()

def reset_password_for_user(id_pengguna, new_password):
    try:
        cur = mysql.connection.cursor()
        pw_hash = generate_password_hash(new_password)
        cur.execute("UPDATE pengguna SET password_hash = %s WHERE id_pengguna = %s", (pw_hash, id_pengguna))
        mysql.connection.commit()
        cur.close()
        return True
    except Exception as e:
        print('reset_password_for_user error:', e)
        return False
