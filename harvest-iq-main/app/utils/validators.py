import re

def validate_phone(phone):
    pattern = r'^(09|\+639)\d{9}$'
    return bool(re.match(pattern, phone))

def validate_password_strength(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number."
    return True, "OK"

def validate_price(price):
    try:
        p = float(price)
        return p > 0
    except (ValueError, TypeError):
        return False

def sanitize_search(query):
    return re.sub(r'[^\w\s\-]', '', query).strip()[:100]