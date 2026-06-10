import logging
from datetime import datetime
from jsonrpcserver import method, Result, Success, Error as RpcError

from cards.models import Card
from cards.utils import parse_expire, format_card
from .models import Transfer
from .utils import (
    generate_otp,
    send_telegram_message,
    validate_card,
    calculate_exchange,
    get_transfer_by_ext_id,
)

logger = logging.getLogger(__name__)


@method(name="transfer.create")
def transfer_create(ext_id, sender_card_number, sender_card_expiry,
                    receiver_card_number, sending_amount, currency) -> Result:
    try:
        if Transfer.objects.filter(ext_id=ext_id).exists():
            return RpcError(32701, "Ext id already exists")

        if currency not in [643, 840]:
            return RpcError(32707, "Currency not allowed except 860, 643, 840")

        if not validate_card(sender_card_number):
            return RpcError(32704, "Card expiry is not valid")

        try:
            expire = parse_expire(sender_card_expiry)
            formatted_sender = format_card(sender_card_number)
            sender_card = Card.objects.get(
                card_number=formatted_sender,
                expire=expire
            )
        except Card.DoesNotExist:
            return RpcError(32704, "Card expiry is not valid")

        if sender_card.status != "active":
            return RpcError(32705, "Card is not active")

        if sender_card.balance < sending_amount:
            return RpcError(32702, "Balance is not enough")

        formatted_receiver = format_card(receiver_card_number)
        if not Card.objects.filter(card_number=formatted_receiver).exists():
            return RpcError(32705, "Card is not active")

        receiving_amount = calculate_exchange(sending_amount, currency)
        otp = generate_otp()

        transfer = Transfer.objects.create(
            ext_id=ext_id,
            sender_card_number=formatted_sender,
            receiver_card_number=formatted_receiver,
            sender_card_expiry=expire,
            sender_phone=sender_card.phone,
            receiver_phone=None,
            sending_amount=sending_amount,
            currency=currency,
            receiving_amount=receiving_amount,
            otp=otp,
            state=Transfer.State.CREATED,
        )

        message = f"Your OTP for transfer {ext_id}: {otp}"
        otp_sent = send_telegram_message(message)

        logger.info(f"Transfer created: {ext_id}, OTP sent: {otp_sent}")

        return Success({
            "ext_id": transfer.ext_id,
            "state": transfer.state,
            "otp_sent": otp_sent,
        })

    except Exception as e:
        logger.error(f"transfer.create error: {e}")
        return RpcError(32706, "Unknown error occurred")


@method(name="transfer.confirm")
def transfer_confirm(ext_id, otp) -> Result:
    try:
        transfer = get_transfer_by_ext_id(ext_id)
        if not transfer:
            return RpcError(32700, "Ext id must be unique")

        if transfer.state != Transfer.State.CREATED:
            return RpcError(32713, "Method is not allowed")

        if transfer.try_count >= 3:
            return RpcError(32711, "Count of try is reached")

        if transfer.otp != otp:
            transfer.try_count += 1
            transfer.save()
            left = 3 - transfer.try_count
            return RpcError(32712, f"OTP is wrong, left try count is {left}")

        transfer.state = Transfer.State.CONFIRMED
        transfer.confirmed_at = datetime.now()
        transfer.save()

        logger.info(f"Transfer confirmed: {ext_id}")

        return Success({
            "ext_id": transfer.ext_id,
            "state": transfer.state,
        })

    except Exception as e:
        logger.error(f"transfer.confirm error: {e}")
        return RpcError(32706, "Unknown error occurred")


@method(name="transfer.cancel")
def transfer_cancel(ext_id) -> Result:
    try:
        transfer = get_transfer_by_ext_id(ext_id)
        if not transfer:
            return RpcError(32700, "Ext id must be unique")

        if transfer.state != Transfer.State.CREATED:
            return RpcError(32713, "Method is not allowed")

        transfer.state = Transfer.State.CANCELLED
        transfer.cancelled_at = datetime.now()
        transfer.save()

        logger.info(f"Transfer cancelled: {ext_id}")

        return Success({"state": transfer.state})

    except Exception as e:
        logger.error(f"transfer.cancel error: {e}")
        return RpcError(32706, "Unknown error occurred")


@method(name="transfer.state")
def transfer_state(ext_id) -> Result:
    try:
        transfer = get_transfer_by_ext_id(ext_id)
        if not transfer:
            return RpcError(32700, "Ext id must be unique")

        return Success({
            "ext_id": transfer.ext_id,
            "state": transfer.state,
        })

    except Exception as e:
        logger.error(f"transfer.state error: {e}")
        return RpcError(32706, "Unknown error occurred")


@method(name="transfer.history")
def transfer_history(card_number=None, start_date=None, end_date=None, status=None) -> Result:
    try:
        qs = Transfer.objects.all()

        if card_number:
            formatted = format_card(card_number)
            qs = Transfer.objects.filter(sender_card_number=formatted) | \
                 Transfer.objects.filter(receiver_card_number=formatted)

        if start_date:
            qs = qs.filter(created_at__date__gte=start_date)

        if end_date:
            qs = qs.filter(created_at__date__lte=end_date)

        if status:
            qs = qs.filter(state=status)

        result = [
            {
                "ext_id": t.ext_id,
                "sending_amount": float(t.sending_amount),
                "state": t.state,
                "created_at": t.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
            }
            for t in qs
        ]

        return Success(result)

    except Exception as e:
        logger.error(f"transfer.history error: {e}")
        return RpcError(32706, "Unknown error occurred")