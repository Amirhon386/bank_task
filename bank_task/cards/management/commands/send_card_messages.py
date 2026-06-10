from django.core.management.base import BaseCommand

from cards.models import Card
from cards.utils import prepare_message, send_message


class Command(BaseCommand):
    help = "Send fake messages to filtered cards"

    def add_arguments(self, parser):
        parser.add_argument("--status", type=str)
        parser.add_argument("--card_number", type=str)
        parser.add_argument("--phone", type=str)
        parser.add_argument("--lang", type=str, default="UZ")

    def handle(self, *args, **options):
        cards = Card.objects.all()

        if options["status"]:
            cards = cards.filter(status=options["status"])

        if options["card_number"]:
            cards = cards.filter(card_number__icontains=options["card_number"])

        if options["phone"]:
            cards = cards.filter(phone__icontains=options["phone"])

        count = 0

        for card in cards:
            message = prepare_message(card.card_number, card.balance, options["lang"])
            send_message(message, chat_id=1666488077)
            self.stdout.write(self.style.SUCCESS(f"Sent: {card.card_number}"))
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Total sent: {count}"))