import smtplib
import os
from email.mime.text import MIMEText
from pathlib import Path


def send_email_alert(objects):
    email_address = os.getenv("ALERT_EMAIL_ADDRESS")
    email_password = os.getenv("ALERT_EMAIL_PASSWORD")
    to_email = os.getenv("ALERT_TO_EMAIL")

    if not email_address or not email_password or not to_email:
        print("⚠️ Email alert skipped: set ALERT_EMAIL_ADDRESS, ALERT_EMAIL_PASSWORD, and ALERT_TO_EMAIL")
        return

    subject = "🚨 Security Alert!"
    body = f"Detected dangerous objects: {objects}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = email_address
    msg["To"] = to_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(msg)

        print("📧 Email sent!")
    except Exception as e:
        print("❌ Email failed:", e)