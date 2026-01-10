import logging
from ..config import config, SMTP_USERNAME, SMTP_PASSWORD, SMTP_SERVER, SMTP_PORT
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


def send_verification_email(email: str, username: str, token: str):
    """Send verification email to user"""
    try:
        # Create verification URL
        verification_url = f"{config.ALLOW_ORIGINS}/verify-email?token={token}"

        # Read HTML template
        template_path = os.path.join("src", "templates", "verification_email.html")
        with open(template_path, "r", encoding="utf-8") as file:
            body = file.read()
        body = body.replace("{{username}}", username)
        body = body.replace("{{verification_url}}", verification_url)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Verify Your Weather Bot Account"
        msg['From'] = SMTP_USERNAME
        msg['To'] = email

        # Attach HTML content
        html_part = MIMEText(body, 'html')
        msg.attach(html_part)

        # Send email
        if SMTP_USERNAME and SMTP_PASSWORD:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)

            logging.info(f"Verification email sent to {email}")
        else:
            logging.warning(f"Email not configured. Verification link: {verification_url}")
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
