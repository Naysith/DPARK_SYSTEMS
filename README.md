# Delis Park

## Description

Proyek ini adalah sistem manajemen tiket berbasis website bernama Delis Park. Sistem ini dirancang untuk memberikan transparansi informasi, meningkatkan efisiensi operasional, dan memberikan pengalaman yang lebih baik bagi pengunjung tempat wisata.

* **Pelanggan** dapat melihat informasi detail wahana, melakukan reservasi, dan membayar tiket secara online.
* **Admin** dapat mengelola data master (wahana, sesi, harga), mengelola akun pengguna (Staff dan Pelanggan), dan melihat laporan penjualan.
* **Staff** dapat melakukan validasi tiket pengunjung di pintu masuk.

## Tech Stack

* **Backend:** Python, Flask
* **Frontend:** Tailwind CSS
* **Database:** MySQL
* **Web Server:** Apache
* **Lingkungan Pendukung:** Node.js (NPM) (untuk dependensi frontend), XAMPP/Laragon (untuk Apache & MySQL)

## Architecture Pattern

Aplikasi ini dibangun menggunakan arsitektur **MVC (Model, View, Controller)**. Pola ini dipilih untuk menciptakan pemisahan tanggung jawab (*separation of concerns*) yang jelas, di mana setiap komponen aplikasi dipisahkan berdasarkan fungsinya. Hal ini membuat kode lebih terorganisir, skalabel, dan mudah dikelola.

## Project Structure (Simplified)

* `DelisPark/`
    * `app/`
        * `controllers/`: Menangani permintaan (request) dan rute (routing).
        * `models/`: Berisi definisi model data dan logika interaksi database.
        * `templates/`: Berisi semua file template HTML yang ditampilkan ke pengguna.
        * `utils/`: Menyimpan fungsi-fungsi pembantu (utility/helper).
    * `.gitignore`: Menentukan file/folder yang diabaikan oleh Git.
    * `config.py`: File konfigurasi pusat (kunci rahasia, URI database).
    * `init_db.py`: Skrip untuk inisialisasi database dan membuat tabel.
    * `run.py`: File eksekusi utama untuk menjalankan server aplikasi.

## Installation

Untuk menjalankan proyek ini di mesin lokal Anda, ikuti langkah-langkah berikut:

1.  **Clone repositori:**
    ```bash
    git clone -b master https://github.com/Naysith/DPARK_SYSTEMS/
    cd DPARK-SYSTEMS # (atau nama folder yang sesuai)
    ```
    

2.  **Install dependensi frontend (Tailwind CSS):**
    ```bash
    npm install
    ```
    

3.  **Install dependensi Python (Flask):**
    ```bash
    pip install -r requirements.txt
    ```
   

## Setup

1.  **Nyalakan Layanan Database:**
    Buka XAMPP/Laragon Control Panel dan nyalakan (Start) layanan **Apache** dan **MySQL**.

2.  **Konfigurasi Database:**
    * Buka browser dan navigasikan ke `http://localhost/phpmyadmin`.
    * Buat database baru dengan nama `delispark`.
    * Klik tab "Import". Jika file `.sql` tersedia, impor file tersebut. Jika tidak, Anda mungkin perlu membuat tabel secara manual berdasarkan LRS yang ada di dokumentasi.

3.  **Konfigurasi Proyek:**
    * Buka file `config.py` di editor Anda.
    * Sesuaikan pengaturan koneksi database agar sesuai dengan konfigurasi database `delispark` Anda.

4.  **Menjalankan Aplikasi (Gunakan 2 Terminal):**

    * **Terminal 1 - Compile CSS:**
        Jalankan perintah ini untuk meng-compile Tailwind CSS:
        ```bash
        npx @tailwindcss/cli -i ./app/static/src/css/input.css -o ./app/static/src/css/output.css
        ```
   

    * **Terminal 2 - Jalankan Server Flask:**
        Atur mode debug dan jalankan server:
        ```bash
        # Perintah untuk Powershell (mungkin berbeda di terminal lain)
        $env:FLASK_DEBUG=1
        
        # Jalankan server
        flask run
        ```
        

5.  **Akses Aplikasi:**
    Aplikasi web akan berjalan. Buka browser Anda dan akses alamat `http://127.0.0.1:5000/`.

## Authentication

Sistem mengelola autentikasi pengguna dan sesi.

* **Penyimpanan Password:** Kata sandi tidak disimpan sebagai teks biasa (plaintext). Saat registrasi, kata sandi di-hash dan di-salt (misalnya menggunakan `generate_password_hash`).
* **Proses Login:** Selama login, kata sandi yang dikirimkan akan di-hash dan dibandingkan dengan hash yang tersimpan di database (misalnya menggunakan `check_password_hash`).
* **Manajemen Sesi:** Setelah autentikasi berhasil, informasi penting pengguna (seperti id, nama, dan peran) disimpan ke dalam objek `session` yang disediakan oleh Flask. Proses logout akan menghapus data dari sesi (`session.clear()`).

## Alur Kerja Sistem (User Flow)

### Alur Pelanggan
![USERFLOW](/app/static/src/images/DelisPark_Customer_FlowChart.png)

### Alur Staff
![USERFLOW](/app/static/src/images/DelisPark_Staff_FlowChart.png)

### Alur Admin
![USERFLOW](/app/static/src/images/DelisPark_admin_Flowchart.png)

## Entity Relationship Diagram (ERD)

![ERD](/app/static/src/images/DelisPark_ERD.png)

## logical Record Structure (LRS)

![LRS](/app/static/src/images/DelisPark_LRS.png)
