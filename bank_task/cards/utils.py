import re
from datetime import date
from decimal import Decimal,InvalidOperation

def only_digits(value:str) -> str:
    if not value:
        return ""
    return re.sub(r"\D","",str(value))

def format_card(raw_card:str) -> str:
    digits = only_digits(raw_card)
    if len(digits) != 16:
        raise ValueError("the card number you need is exactly 16")
    result = []
    for i in range(0, 16, 4):
        group = digits[i:i + 4]
        result.append(group)

    return " ".join(result)

def card_mask(card_number:str)->str:
    digits = only_digits(card_number)
    if len(digits) != 16:
        return card_number
    return f"{digits[:4]} **** **** {digits[-4:]}"

def format_phone(raw_phone:str)->str:
    if raw_phone is None:
        return ""
    digits = only_digits(raw_phone)

    if not digits:
        return ""
    if len (digits) == 7:
        digits = "99" + digits

    if len(digits) != 9:
        raise ValueError("the phone number must be 9 digits long or empty")
    
    return f"{digits[0:2]} {digits[2:5]} {digits[5:7]} {digits[7:9]}"

def phone_mask(phone:str)->str:
    digits = only_digits(phone)
    if len(digits) != 9:
        return phone or ""
    return f"{digits[:2]} *** ** {digits[-2:]}"

def parse_expire(raw_expire:str)->date:
    if not raw_expire:
        raise ValueError("expire is required")
    
    value = str(raw_expire).strip()

    match = re.fullmatch(r"(\d{2})/(\d{2})", value)

    if match:
        month,year = match.groups()
        month = int(month)
        year = 2000 + int(year)
        if not 1 <= month <= 12:
            raise ValueError("invalid month")
        return date(year,month, 1)
    
    match = re.fullmatch(r"(\d{4})-(\d{2})", value)
    if match:
        year, month = match.groups()
        year = int(year)
        month = int(month)
        if not 1 <= month <= 12:
            raise ValueError("invalid month")
        return date(year, month, 1)
    
    match = re.fullmatch(r"(\d{2})\.(\d{4})", value)
    if match:
        month, year = match.groups()
        month = int(month)
        year = int(year)
        if not 1 <= month <= 12:
            raise ValueError("Invalid month")
        return date(year, month, 1)

    raise ValueError(f"Unsupported expire format: {value}")


def parse_balance(raw_balance) -> Decimal:
    if raw_balance is None or raw_balance == "":
        raise ValueError("Balance is required")

    value = str(raw_balance).replace(",", "").strip()

    try:
        balance = Decimal(value)
    except InvalidOperation:
        raise ValueError("Invalid balance format")

    if balance < 0:
        raise ValueError("Balance cannot be negative")

    if balance > Decimal("1200000000.00"):
        raise ValueError("Balance cannot exceed 1.2 billion UZS")

    return balance


def normalize_status(raw_status: str) -> str:
    if not raw_status:
        raise ValueError("Status is required")

    value = str(raw_status).strip().lower()
    if value not in {"active", "inactive", "expired"}:
        raise ValueError("Invalid status")

    return value


def prepare_message(card_number, balance, lang="UZ"):
    if lang.upper() == "UZ":
        return f"Sizning kartangiz {card_mask(card_number)} aktiv va foydalanishga {balance} UZS mavjud!"
    return f"Your card {card_mask(card_number)} is active and has {balance} UZS available!"


def send_message(message, chat_id=12345):
    print(f"[FAKE TELEGRAM] chat_id={chat_id} | {message}")
    return True