from flask import Flask
from flask_mysqldb import MySQL
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)


# --- Your schema creation SQL ---
schema = """
CREATE TABLE IF NOT EXISTS pengguna (
    id_pengguna INT AUTO_INCREMENT PRIMARY KEY,
    nama_pengguna VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    peran ENUM('admin','staff','pelanggan') NOT NULL,
    nomor_telepon VARCHAR(20),
    alamat_rumah VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS wahana (
    id_wahana INT AUTO_INCREMENT PRIMARY KEY,
    nama_wahana VARCHAR(100) NOT NULL,
    deskripsi TEXT,
    status_wahana ENUM('aktif','nonaktif') DEFAULT 'aktif',
    gambar_wahana LONGBLOB
);

CREATE TABLE IF NOT EXISTS sesi (
    id_sesi INT AUTO_INCREMENT PRIMARY KEY,
    id_wahana INT NOT NULL,
    nama_sesi VARCHAR(100),
    kuota INT,
    harga INT,
    waktu_mulai DATETIME,
    waktu_selesai DATETIME,
    FOREIGN KEY (id_wahana) REFERENCES wahana(id_wahana)
);

CREATE TABLE IF NOT EXISTS reservasi (
    id_reservasi INT AUTO_INCREMENT PRIMARY KEY,
    id_pengguna INT NOT NULL,
    tanggal_reservasi DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_harga INT,
    status_pembayaran ENUM('menunggu','selesai') DEFAULT 'menunggu',
    kode_unik VARCHAR(50),
    FOREIGN KEY (id_pengguna) REFERENCES pengguna(id_pengguna)
);

CREATE TABLE IF NOT EXISTS pembayaran (
    id_pembayaran INT AUTO_INCREMENT PRIMARY KEY,
    id_reservasi INT NOT NULL,
    tanggal_bayar DATETIME DEFAULT CURRENT_TIMESTAMP,
    jumlah_bayar INT,
    metode_pembayaran ENUM('BANK','QRIS'),
    FOREIGN KEY (id_reservasi) REFERENCES reservasi(id_reservasi) ON DELETE CASCADE

);

CREATE TABLE IF NOT EXISTS tiket (
    id_tiket INT AUTO_INCREMENT PRIMARY KEY,
    id_reservasi INT NOT NULL,
    id_sesi INT NOT NULL,
    kode_tiket VARCHAR(50) UNIQUE,
    status_tiket ENUM('belum_digunakan','sudah_digunakan') DEFAULT 'belum_digunakan',
    FOREIGN KEY (id_reservasi) REFERENCES reservasi(id_reservasi),
    FOREIGN KEY (id_sesi) REFERENCES sesi(id_sesi)
);

CREATE TABLE IF NOT EXISTS validasi (
    id_validasi INT AUTO_INCREMENT PRIMARY KEY,
    id_pengguna INT NOT NULL,
    id_wahana INT NOT NULL,
    waktu_validasi DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_pengguna) REFERENCES pengguna(id_pengguna),
    FOREIGN KEY (id_wahana) REFERENCES wahana(id_wahana)
);
"""

@app.cli.command("init-db")
def init_db():
    """Create all tables."""
    cur = mysql.connection.cursor()
    for statement in schema.split(";"):
        stmt = statement.strip()
        if stmt:
            cur.execute(stmt)
    mysql.connection.commit()
    cur.close()
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    with app.app_context():
        init_db()