from datetime import date, datetime

def calculate_status(expiry_date: date):
    today = date.today()
    days_until_expiry = (expiry_date - today).days

    if days_until_expiry < 0:
        return "Expired", days_until_expiry
    elif days_until_expiry <= 7:
        return "Expiring Soon", days_until_expiry
    else:
        return "Fresh", days_until_expiry
