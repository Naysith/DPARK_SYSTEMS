import smtplib
from email.message import EmailMessage

# Replace with your SMTP server info
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "youremail@gmail.com"
EMAIL_PASSWORD = "your_app_password"  # Use app password if Gmail

def send_email(to, subject, body, attachments=[]):
    """
    Sends an email with optional attachments.
    """
    msg = EmailMessage()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to
    msg['Subject'] = subject
    msg.set_content(body)

    # Attach files
    for filepath in attachments:
        with open(filepath, 'rb') as f:
            file_data = f.read()
            file_name = filepath.split("/")[-1]
            msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)
    
    # Send email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

    print(f"📧 Email sent to {to} with {len(attachments)} attachment(s).")
    