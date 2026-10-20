import os
import smtplib
from email.message import EmailMessage

def email_is_configured():
    return all(os.getenv(k) for k in ("SMTP_USERNAME", "SMTP_APP_PASSWORD", "ALERT_TO_EMAIL"))

def send_email(subject, body):
    username = os.environ["SMTP_USERNAME"]
    password = os.environ["SMTP_APP_PASSWORD"]
    recipient = os.environ["ALERT_TO_EMAIL"]

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = username
    message["To"] = recipient
    message.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
        smtp.login(username, password)
        smtp.send_message(message)
