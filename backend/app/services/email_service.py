import smtplib
from email.mime.text import MIMEText

EMAIL_ADDRESS = "shehantharushe@gmail.com"
EMAIL_PASSWORD = "qrht tvww nymi eqak"
TO_EMAIL = "shehanjaya1921@gmail.com"

def send_email_alert(objects):
    subject = "🚨 Security Alert!"
    body = f"Detected dangerous objects: {objects}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        print("📧 Email sent!")
    except Exception as e:
        print("❌ Email failed:", e)