from app import mysql
from app.utils.tiket_pdf import generate_ticket_pdf
from app.utils.send_email import send_email


def add_pembayaran(id_reservasi, form):
    """Create a pembayaran record, update reservasi status, generate PDF tickets.
    Does NOT auto-send email. Returns a dict with keys: id_pembayaran, pdf_file, email_to, nama_user.
    """
    pdf_file = None
    jumlah = int(form['jumlah_bayar'])
    metode = form['metode_pembayaran']

    cur = mysql.connection.cursor()

    # --- Insert payment ---
    cur.execute("""
        INSERT INTO pembayaran (id_reservasi, jumlah_bayar, metode_pembayaran)
        VALUES (%s, %s, %s)
    """, (id_reservasi, jumlah, metode))
    id_pembayaran = cur.lastrowid

    # --- Update reservation status ---
    cur.execute("""
        UPDATE reservasi
        SET status_pembayaran = 'selesai'
        WHERE id_reservasi = %s
    """, (id_reservasi,))

    # --- Fetch tickets and user info ---
    cur.execute("""
        SELECT t.kode_tiket, t.status_tiket, w.nama_wahana, s.nama_sesi, u.email, u.nama_pengguna
        FROM tiket t
        JOIN sesi s ON t.id_sesi = s.id_sesi
        JOIN wahana w ON s.id_wahana = w.id_wahana
        JOIN reservasi r ON t.id_reservasi = r.id_reservasi
        JOIN pengguna u ON r.id_pengguna = u.id_pengguna
        WHERE r.id_reservasi = %s
    """, (id_reservasi,))
    tiket_list = cur.fetchall()

    # --- Generate PDF (do not send yet) ---
    email_to = None
    nama_user = None
    if tiket_list:
        email_to = tiket_list[0][4]
        nama_user = tiket_list[0][5]
        filepath, public_url = generate_ticket_pdf(tiket_list, id_reservasi, nama_user)
        pdf_file = public_url

    # --- Commit changes and close cursor ---
    mysql.connection.commit()
    cur.close()

    return {
        'id_pembayaran': id_pembayaran,
        'pdf_file': pdf_file,
        'pdf_filepath': filepath if tiket_list else None,
        'email_to': email_to,
        'nama_user': nama_user
    }
