from datetime import date,timedelta, datetime, timezone
import logging
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.user import User
from app.services.email import send_expiry_reminder

logger = logging.getLogger("expiry_tracker.tasks")

def calculate_status(expiry_date: date):
    today = date.today()
    days_until_expiry = (expiry_date - today).days

    if days_until_expiry < 0:
        return "Expired", days_until_expiry
    elif days_until_expiry <= 7:
        return "Expiring Soon", days_until_expiry
    else:
        return "Fresh", days_until_expiry

# check expiry reminders
def check_and_send_expiry_reminders(db: Session) -> dict:
    today = date.today()
    target_date = today + timedelta(days=7)

    products_to_remind = (
        db.query(Product)
        .join(User, Product.user_id == User.id)
        .filter(
           Product.expiry_date <= target_date,
           Product.expiry_date >= today,
           Product.reminder_sent == False
        ).all()
    )

    sent_count = 0
    for product in products_to_remind:
        user = product.owner
        if user and user.email:
            format_date = product.expiry_date.strftime("%d %B %Y")
            success = send_expiry_reminder(
               user_name=user.username,
               user_email=user.email,
               product_name=product.name,
               expiry_date_str=format_date
            )
            if success:
                product.reminder_sent = True
                sent_count += 1

    if sent_count > 0:
        db.commit()
        logger.info(f"Sent {sent_count} expiry reminder(s).")

    return {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "reminders_sent": sent_count,
        "eligible_products": len(products_to_remind),
    }
