from app import mysql
from flask import flash, redirect, url_for
from app.utils.error_handler import handle_mysql_error
from uuid import uuid4

def dictfetchall(cursor):
    """Convert all rows from cursor to list of dicts"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

# ======================================================
# 🟢 GET RESERVATIONS (BY USER)
# ======================================================
def get_reservasi_by_user(id_pengguna):
    cur = mysql.connection.cursor()
    query = """
        SELECT 
            r.*, 
            w.nama_wahana, 
            s.waktu_mulai, 
            s.waktu_selesai, 
            s.kuota
        FROM reservasi r
        -- join via tiket since reservasi doesn't store id_sesi directly
        JOIN tiket t ON t.id_reservasi = r.id_reservasi
        JOIN sesi s ON t.id_sesi = s.id_sesi
        JOIN wahana w ON s.id_wahana = w.id_wahana
        WHERE r.id_pengguna = %s
        ORDER BY r.id_reservasi DESC
    """
    cur.execute(query, (id_pengguna,))
    data = dictfetchall(cur)
    cur.close()
    # Always return a list (empty if no rows) to make templates safe.
    return data or []



# ======================================================
# 🟢 GET ALL RESERVATIONS (ADMIN VIEW)
# ======================================================
def get_all_reservasi():
    cur = mysql.connection.cursor()
    query = """
        SELECT r.*, u.nama_pengguna, s.nama_sesi, w.nama_wahana
        FROM reservasi r
        JOIN pengguna u ON r.id_pengguna = u.id_pengguna
        JOIN tiket t ON t.id_reservasi = r.id_reservasi
        JOIN sesi s ON t.id_sesi = s.id_sesi
        JOIN wahana w ON s.id_wahana = w.id_wahana
        ORDER BY r.id_reservasi DESC
    """
    cur.execute(query)
    data = dictfetchall(cur)
    cur.close()
    return data or []


# ======================================================
# 🟢 ADD RESERVATION
# ======================================================
def add_reservasi(id_pengguna, id_sesi, jumlah_tiket, status_pembayaran='menunggu'):
    try:
        cur = mysql.connection.cursor()

        # 🔍 Validate session existence
        cur.execute("SELECT kuota, harga FROM sesi WHERE id_sesi = %s", (id_sesi,))
        sesi_data = cur.fetchone()
        if not sesi_data:
            flash('❌ Sesi tidak ditemukan.', 'danger')
            cur.close()
            return False
        kapasitas_tersisa = sesi_data[0]
        harga_per_tiket = sesi_data[1] if len(sesi_data) > 1 else 0
        if kapasitas_tersisa < int(jumlah_tiket):
            flash('❌ Kapasitas sesi tidak mencukupi!', 'danger')
            cur.close()
            return False

        # 🔍 Prevent duplicate reservation for same user & sesi via tiket join
        cur.execute("""
            SELECT t.id_tiket FROM tiket t
            JOIN reservasi r ON t.id_reservasi = r.id_reservasi
            WHERE r.id_pengguna = %s AND t.id_sesi = %s
        """, (id_pengguna, id_sesi))
        if cur.fetchone():
            flash('❌ Reservasi untuk sesi ini sudah ada!', 'danger')
            cur.close()
            return False

        # 🟢 Insert new reservation: store total_harga and a kode_unik
        total_harga = int(jumlah_tiket) * int(harga_per_tiket)
        kode_unik = uuid4().hex[:10]
        cur.execute("""
            INSERT INTO reservasi (id_pengguna, total_harga, status_pembayaran, kode_unik)
            VALUES (%s, %s, %s, %s)
        """, (id_pengguna, total_harga, status_pembayaran, kode_unik))
        new_res_id = cur.lastrowid

        # Insert tiket rows (one per tiket) linking to sesi
        for i in range(int(jumlah_tiket)):
            kode_tiket = f"{kode_unik}-{i+1}"
            cur.execute("INSERT INTO tiket (id_reservasi, id_sesi, kode_tiket) VALUES (%s, %s, %s)",
                        (new_res_id, id_sesi, kode_tiket))

        # 🟡 Decrease capacity (kuota)
        cur.execute("UPDATE sesi SET kuota = kuota - %s WHERE id_sesi = %s", (jumlah_tiket, id_sesi))

        mysql.connection.commit()
        cur.close()
        flash('✅ Reservasi berhasil ditambahkan!', 'success')
        return True

    except Exception as e:
        return handle_mysql_error(e, 'reservasi_bp.reservasi_list')


# ======================================================
# 🟢 EDIT RESERVATION
# ======================================================
def edit_reservasi(id_reservasi, form):
    id_sesi = form['id_sesi']
    jumlah_tiket = int(form['jumlah_tiket'])
    status_pembayaran = form['status_pembayaran']

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE reservasi 
        SET id_sesi=%s, jumlah_tiket=%s, status_pembayaran=%s
        WHERE id_reservasi=%s
    """, (id_sesi, jumlah_tiket, status_pembayaran, id_reservasi))
    mysql.connection.commit()
    cur.close()
    flash('✅ Reservasi berhasil diperbarui!', 'success')
    return redirect(url_for('reservasi_bp.reservasi_list'))


# ======================================================
# 🟢 DELETE RESERVATION
# ======================================================
def delete_reservasi(id_reservasi):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM reservasi WHERE id_reservasi = %s", (id_reservasi,))
    mysql.connection.commit()
    cur.close()
    flash('🗑️ Reservasi berhasil dihapus!', 'success')
    return redirect(url_for('reservasi_bp.reservasi_list'))


# ======================================================
# 🟢 GET SINGLE RESERVATION
# ======================================================
def get_reservasi(id_reservasi):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM reservasi WHERE id_reservasi = %s", (id_reservasi,))
    row = cur.fetchone()
    data = {}
    if row:
        columns = [col[0] for col in cur.description]
        data = dict(zip(columns, row))
    cur.close()
    return data


def add_reservasi_return_id(id_pengguna, id_sesi, jumlah_tiket, status_pembayaran='menunggu'):
    """Create reservation and return new id_reservasi. Performs same checks as add_reservasi."""
    try:
        cur = mysql.connection.cursor()

        # Validate session existence and kuota
        cur.execute("SELECT kuota, harga FROM sesi WHERE id_sesi = %s", (id_sesi,))
        sesi_data = cur.fetchone()
        if not sesi_data:
            return None

        kapasitas_tersisa = sesi_data[0]
        harga_per_tiket = sesi_data[1] if len(sesi_data) > 1 else 0
        if kapasitas_tersisa < int(jumlah_tiket):
            return None

        # Prevent duplicate via tiket/reservasi join
        cur.execute("""
            SELECT t.id_tiket FROM tiket t
            JOIN reservasi r ON t.id_reservasi = r.id_reservasi
            WHERE r.id_pengguna=%s AND t.id_sesi=%s
        """, (id_pengguna, id_sesi))
        if cur.fetchone():
            return None

        # Insert reservation
        total_harga = int(jumlah_tiket) * int(harga_per_tiket)
        kode_unik = uuid4().hex[:10]
        cur.execute("INSERT INTO reservasi (id_pengguna, total_harga, status_pembayaran, kode_unik) VALUES (%s,%s,%s,%s)",
                    (id_pengguna, total_harga, status_pembayaran, kode_unik))
        new_id = cur.lastrowid

        # Insert tiket rows
        for i in range(int(jumlah_tiket)):
            kode_tiket = f"{kode_unik}-{i+1}"
            cur.execute("INSERT INTO tiket (id_reservasi, id_sesi, kode_tiket) VALUES (%s, %s, %s)", (new_id, id_sesi, kode_tiket))

        # Decrease kuota
        cur.execute("UPDATE sesi SET kuota = kuota - %s WHERE id_sesi = %s", (jumlah_tiket, id_sesi))

        mysql.connection.commit()
        cur.close()
        return new_id
    except Exception:
        return None
