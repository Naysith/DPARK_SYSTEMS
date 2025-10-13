from flask import flash, redirect, url_for

def handle_mysql_error(e, redirect_to):
    """
    Handles MySQL exceptions with user-friendly flash messages.
    Automatically detects duplicate key errors.
    """
    print(f"[MYSQL ERROR] {e}")

    msg = str(e)
    if "Duplicate entry" in msg:
        flash("❌ Data duplikat: Nilai tersebut sudah digunakan.", "danger")
    elif "foreign key constraint" in msg.lower():
        flash("⚠️ Tidak dapat menghapus data karena sedang digunakan di tabel lain.", "warning")
    else:
        flash("⚠️ Terjadi kesalahan pada database. Silakan coba lagi.", "danger")

    return redirect(url_for(redirect_to))
