from fpdf import FPDF
import os
from reportlab.lib.utils import ImageReader
from app import PDF_FOLDER
from PIL import Image

def generate_ticket_pdf(tiket_list, reservasi_id, nama_user):
    """
    Generates a PDF file containing QR codes and ticket details.
    Accepts tiket_list as list of dicts:
        {
            "kode_tiket": "...",
            "status_tiket": "...",
            "nama_wahana": "...",
            "nama_sesi": "...",
            "qr_buf": <BytesIO>,
        }
    """

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for t in tiket_list:
        kode_tiket = t["kode_tiket"]
        status_tiket = t["status_tiket"]
        wahana = t["nama_wahana"]
        sesi = t["nama_sesi"]
        qr_buf = t["qr_buf"]

        # Convert QR buffer → temp PNG path
        qr_img = Image.open(qr_buf)
        temp_qr_path = f"/tmp/qr_{kode_tiket}.png"
        qr_img.save(temp_qr_path)

        pdf.add_page()

        # Title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "DelisPark Ticket", ln=True, align="C")

        pdf.ln(10)
        pdf.set_font("Arial", '', 12)

        # Text info
        pdf.cell(0, 10, f"Nama Pengunjung: {nama_user}", ln=True)
        pdf.cell(0, 10, f"Wahana: {wahana}", ln=True)
        pdf.cell(0, 10, f"Sesi: {sesi}", ln=True)
        pdf.cell(0, 10, f"Kode Tiket: {kode_tiket}", ln=True)
        pdf.cell(0, 10, f"Status: {status_tiket}", ln=True)

        pdf.ln(5)

        # Insert QR code image
        pdf.image(temp_qr_path, x=10, y=80, w=50)

        # Clean temp file
        try:
            os.remove(temp_qr_path)
        except:
            pass

    # Save final PDF
    filename = f"tiket_{reservasi_id}.pdf"
    filepath = os.path.join(PDF_FOLDER, filename)
    pdf.output(filepath)

    # public URL path for <img> or download
    public_url = f"/static/tickets/{filename}"

    return filepath, public_url


