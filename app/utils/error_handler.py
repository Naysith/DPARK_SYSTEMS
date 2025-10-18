from flask import flash, redirect, url_for

def handle_mysql_error(e, route_name):
    import traceback
    print("MYSQL ERROR:", e)
    traceback.print_exc()  # 👈 shows full stack trace
    flash("⚠️ Terjadi kesalahan pada database. Silakan coba lagi.", "danger")
    return redirect(url_for(route_name))

