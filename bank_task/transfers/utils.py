import random
import requests
from cards.models import Card
from cards.utils import only_digits
from .models import Transfer


def generate_otp(length=6):
    return str(random.randint(100000, 999999))


def send_telegram_message(message, chat_id=1666488077):
    token = "8435344415:AAFpcgIo561gex0ObaKi7wJZSzopNTzvfwo"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(url, data={
        "chat_id": chat_id,
        "text": message
    })
    return response.status_code == 200


def validate_card(card_number):
    digits = only_digits(card_number)
    if len(digits) != 16:
        return False
    total = 0
    for i, digit in enumerate(reversed(digits)):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def calculate_exchange(amount, currency):
    rates = {
        643: 0.011,   # RUB -> UZS
        840: 12600,   # USD -> UZS
    }
    rate = rates.get(currency)
    if rate is None:
        return None
    return round(amount * rate, 2)


def get_transfer_by_ext_id(ext_id):
    try:
        return Transfer.objects.get(ext_id=ext_id)
    except Transfer.DoesNotExist:
        return None