import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

from app.config.email import email_settings

load_dotenv()
logger = logging.getLogger("expiry_tracker.email")


# In-memory log of sent notifications for verification and UI display
sent_emails_log = []


def send_expiry_reminder(user_name: str, user_email: str, product_name: str, expiry_date_str: str) -> bool:
    subject = "Product Expiry Reminder"
    body_text = f"""Hello {user_name},

Your product "{product_name}" will expire in 7 days.

Expiry Date: {expiry_date_str}

Please check the product and use it before it expires.

Product Expiry Tracker"""

    record = {
        "recipient": user_email,
        "recipient_name": user_name,
        "product_name": product_name,
        "expiry_date": expiry_date_str,
        "subject": subject,
        "body": body_text,
    }
    sent_emails_log.append(record)

    if not email_settings.SMTP_ENABLE or not email_settings.SMTP_USERNAME or not email_settings.SMTP_PASSWORD:
        logger.info(f"[SIMULATED EMAIL] To: {user_email} | Subject: {subject} | Product: {product_name}")
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = email_settings.SMTP_FROM
        msg["To"] = user_email

        part = MIMEText(body_text, "plain")
        msg.attach(part)

        with smtplib.SMTP(email_settings.SMTP_SERVER, email_settings.SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(email_settings.SMTP_USERNAME, email_settings.SMTP_PASSWORD)
            server.sendmail(email_settings.SMTP_FROM, [user_email], msg.as_string())

        logger.info(f"Successfully sent reminder email to {user_email} for {product_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {user_email}: {e}")
        return False
