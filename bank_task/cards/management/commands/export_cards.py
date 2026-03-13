import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from cards.models import Card


class Command(BaseCommand):
    help = "Export cards to CSV"

    def add_arguments(self, parser):
        parser.add_argument("--status", type=str)
        parser.add_argument("--card_number", type=str)
        parser.add_argument("--phone", type=str)
        parser.add_argument("--output", type=str, default="cards_export.csv")

    def handle(self, *args, **options):
        qs = Card.objects.all()

        if options["status"]:
            qs = qs.filter(status=options["status"])

        if options["card_number"]:
            qs = qs.filter(card_number__icontains=options["card_number"])

        if options["phone"]:
            qs = qs.filter(phone__icontains=options["phone"])

        output_path = Path(options["output"])

        with output_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["card_number", "expire", "phone", "status", "balance"])

            for card in qs:
                writer.writerow([
                    card.card_number,
                    card.expire.strftime("%Y-%m"),
                    card.phone or "",
                    card.status,
                    card.balance,
                ])

        self.stdout.write(self.style.SUCCESS(f"Exported {qs.count()} cards"))