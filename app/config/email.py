import os
from dotenv import load_dotenv

load_dotenv()

class EmailSettings:
    SMTP_SERVER: str = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    SMTP_FROM: str = os.getenv("SMTP_FROM")
    SMTP_ENABLE: bool = (
        os.getenv("SMTP_ENABLE")
    )

email_settings = EmailSettings()