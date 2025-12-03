import os
from fpdf import FPDF
from PIL import Image

# === Define the PDF output folder here (self-contained) ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_FOLDER = os.path.join(BASE_DIR, "static", "tickets")

# Ensure the folder exists
os.makedirs(PDF_FOLDER, exist_ok=True)


def generate_ticket_pdf(tiket_list, reservasi_id, nama_user):
    """
    Generates a PDF containing QR codes & ticket details.
    """

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    TEMP_QR_DIR = os.path.join(BASE_DIR, "temp_qr")
    os.makedirs(TEMP_QR_DIR, exist_ok=True)

    # Output directory for finished PDFs
    OUTPUT_DIR = os.path.join(os.getcwd(), "app", "static", "tickets")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for t in tiket_list:
        kode_tiket = t["kode_tiket"]
        status_tiket = t["status_tiket"]
        wahana = t["nama_wahana"]
        sesi = t["nama_sesi"]
        qr_buf = t["qr_buf"]

        # Convert QR buffer → image
        qr_img = Image.open(qr_buf)
        temp_qr_path = os.path.join(TEMP_QR_DIR, f"qr_{kode_tiket}.png")
        qr_img.save(temp_qr_path)

        pdf.add_page()

        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "DelisPark Ticket", ln=True, align="C")

        pdf.ln(10)
        pdf.set_font("Arial", "", 12)

        pdf.cell(0, 10, f"Nama Pengunjung: {nama_user}", ln=True)
        pdf.cell(0, 10, f"Wahana: {wahana}", ln=True)
        pdf.cell(0, 10, f"Sesi: {sesi}", ln=True)
        pdf.cell(0, 10, f"Kode Tiket: {kode_tiket}", ln=True)
        pdf.cell(0, 10, f"Status: {status_tiket}", ln=True)

        pdf.ln(5)
        pdf.image(temp_qr_path, x=10, y=80, w=50)

        try:
            os.remove(temp_qr_path)
        except:
            pass

    # ===== Save final PDF =====
    filename = f"tiket_{reservasi_id}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    pdf.output(filepath)

    public_url = f"/static/tickets/{filename}"

    return filepath, public_url