import asyncio
from email.message import EmailMessage

import aiosmtplib

from config.email import email_settings


async def send_test_email():
    if not email_settings.SMTP_ENABLE:
        print("SMTP is disabled.")
        return

    message = EmailMessage()
    message["From"] = email_settings.SMTP_FROM
    message["To"] = email_settings.SMTP_USERNAME
    message["Subject"] = "SMTP Test - Product Expiry Tracker"

    message.set_content(
        "Congratulations! Your SMTP email configuration is working."
    )

    try:
        await aiosmtplib.send(
            message,
            hostname=email_settings.SMTP_SERVER,
            port=email_settings.SMTP_PORT,
            username=email_settings.SMTP_USERNAME,
            password=email_settings.SMTP_PASSWORD,
            start_tls=True,
        )

        print("Test email sent successfully!")

    except Exception as e:
        print(f"Failed to send email: {e}")


if __name__ == "__main__":
    asyncio.run(send_test_email())