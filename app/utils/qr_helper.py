import qrcode, os

def generate_qr(kode_tiket):
    qr_dir = 'app/static/qr_codes'
    os.makedirs(qr_dir, exist_ok=True)
    qr_path = os.path.join(qr_dir, f"{kode_tiket}.png")
    img = qrcode.make(kode_tiket)
    img.save(qr_path)
    return f"/static/qr_codes/{kode_tiket}.png"
