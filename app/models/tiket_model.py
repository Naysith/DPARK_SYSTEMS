from app import mysql
from app.utils.error_handler import handle_mysql_error

def get_tiket(sess):
    try:
        cur = mysql.connection.cursor()
        # Return tiket rows with payment status so the user dashboard can show
        # whether the related reservasi has been paid (status_pembayaran).
        if sess['peran'] == 'admin':
            # Admin sees all tickets; use LEFT JOIN to include possible missing reservasi
            cur.execute("""
                SELECT t.kode_tiket, t.status_tiket, w.nama_wahana, s.nama_sesi, r.status_pembayaran
                FROM tiket t
                LEFT JOIN reservasi r ON t.id_reservasi = r.id_reservasi
                JOIN sesi s ON t.id_sesi = s.id_sesi
                JOIN wahana w ON s.id_wahana = w.id_wahana
                ORDER BY (r.status_pembayaran = 'menunggu') DESC, t.id_tiket DESC
            """)
        else:
            cur.execute("""
                SELECT t.kode_tiket, t.status_tiket, w.nama_wahana, s.nama_sesi, r.status_pembayaran
                FROM tiket t
                JOIN reservasi r ON t.id_reservasi = r.id_reservasi
                JOIN sesi s ON t.id_sesi = s.id_sesi
                JOIN wahana w ON s.id_wahana = w.id_wahana
                WHERE r.id_pengguna = %s
                ORDER BY (r.status_pembayaran = 'menunggu') DESC, t.id_tiket DESC
            """, (sess['id_pengguna'],))
        data = cur.fetchall()
        cur.close()
        return data

    except Exception as e:
        return handle_mysql_error(e, 'user_bp.user_dashboard')

