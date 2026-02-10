import smtplib
from email.message import EmailMessage
import os

EMAIL = os.getenv("EMAIL_USER")
PASSWORD = os.getenv("EMAIL_PASS")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465


def send_mail(to_mail: str, anomalies: list):

    if not anomalies:
        return

    if not EMAIL or not PASSWORD:
        print("Email credentials not set.")
        return

    subject = "🚨 Log Anomaly Detected"

    body = "Anomalies detected in system logs:\n\n"

    for anomaly in anomalies:
        body += f"""
Time Window: {anomaly['timestamp']}
Error Count: {anomaly['error_count']}
Z Score: {anomaly['z_score']}
-------------------------------------
"""

    body += "\nPlease review the system immediately."

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = to_mail
    msg.set_content(body)

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
