import pandas as pd
from .models import Card
from .utils import (format_card,format_phone,normalize_status,parse_balance,parse_expire,luhn_check)

REQUIRED_COLUMNS = {"card_number", "expire", "phone", "status", "balance"}


def import_cards_from_excel(file_obj):
    df = pd.read_excel(file_obj)
    df.columns = df.columns.str.strip()

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")

    created_count = 0
    updated_count = 0
    errors = []

    for index, row in df.iterrows():
        row_number = index + 2

        try:
            raw_card = row.get("card_number")

            if pd.isna(raw_card) or str(raw_card).strip() == "":
                raise ValueError("Card number is empty")

            card_number = format_card(raw_card)

            if not luhn_check(card_number):
                raise ValueError("Card number failed Luhn check")

            expire = parse_expire(row.get("expire"))
            phone = format_phone(row.get("phone"))
            status = normalize_status(row.get("status"))
            balance = parse_balance(row.get("balance"))

            _, created = Card.objects.update_or_create(
                card_number=card_number,
                defaults={
                    "expire": expire,
                    "phone": phone,
                    "status": status,
                    "balance": balance,
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        except Exception as exc:
            errors.append(f"Row {row_number}: {exc}")

    return {
        "created": created_count,
        "updated": updated_count,
        "errors": errors,}