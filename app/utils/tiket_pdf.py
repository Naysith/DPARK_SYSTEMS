from fpdf import FPDF
import os

PDF_FOLDER = "app/static/tickets"
os.makedirs(PDF_FOLDER, exist_ok=True)

def generate_ticket_pdf(tiket_list, reservasi_id, nama_user):
    """
    Generates a PDF file with all tickets for a reservation.
    Returns the filepath.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for tiket in tiket_list:
        kode_tiket, status_tiket, wahana, sesi, _, _ = tiket
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"DelisPark Ticket", ln=True, align="C")
        
        pdf.set_font("Arial", '', 12)
        pdf.ln(10)
        pdf.cell(0, 10, f"Nama Pengunjung: {nama_user}", ln=True)
        pdf.cell(0, 10, f"Wahana: {wahana}", ln=True)
        pdf.cell(0, 10, f"Sesi: {sesi}", ln=True)
        pdf.cell(0, 10, f"Kode Tiket: {kode_tiket}", ln=True)
        pdf.cell(0, 10, f"Status: {status_tiket}", ln=True)

    filename = f"tiket_{reservasi_id}.pdf"
    filepath = os.path.join(PDF_FOLDER, filename)
    pdf.output(filepath)
    # Public URL path for templates
    public_url = f"/static/tickets/{filename}"
    # Return both filesystem path and public URL
    return filepath, public_url
