from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path
from .utils import prepare_message, send_message
from .forms import ExcelImportForm, CardForm
from .models import Card
from .services import import_cards_from_excel
from .utils import card_mask, phone_mask

@admin.action(description="Send message (UZ)")
def send_message_uz(modeladmin, request, queryset):
    for card in queryset:
        message = prepare_message(card.card_number, card.balance, lang="UZ")
        send_message(message, chat_id=1666488077)
    modeladmin.message_user(request, f"Sent to {queryset.count()} cards")


@admin.action(description="Send message (EN)")
def send_message_en(modeladmin, request, queryset):
    for card in queryset:
        message = prepare_message(card.card_number, card.balance, lang="EN")
        send_message(message, chat_id=1666488077)
    modeladmin.message_user(request, f"Sent to {queryset.count()} cards")

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "formatted_card_number",
        "formatted_phone",
        "status",
        "expire",
        "balance",
        "created_at",
    )
    list_filter = ("status", "expire", "phone", "balance")
    search_fields = ("card_number", "phone")
    actions = [send_message_uz, send_message_en]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-excel/",
                self.admin_site.admin_view(self.import_excel_view),
                name="cards_card_import_excel",
            ),
            # 👇 новый роут
            path(
                "luhn-check/",
                self.admin_site.admin_view(self.luhn_check_view),
                name="cards_card_luhn_check",
            ),
        ]
        return custom_urls + urls

    def import_excel_view(self, request):
        if request.method == "POST":
            form = ExcelImportForm(request.POST, request.FILES)
            if form.is_valid():
                result = import_cards_from_excel(form.cleaned_data["file"])

                messages.success(
                    request,
                    f"Created: {result['created']}, Updated: {result['updated']}"
                )

                for err in result["errors"]:
                    messages.error(request, err)

                return redirect("../")
        else:
            form = ExcelImportForm()

        context = {
            "form": form,
            "title": "Import cards from Excel",
        }
        return render(request, "admin/cards/card/import_excel.html", context)

    # 👇 новый view
    def luhn_check_view(self, request):
        result = None
        form = CardForm()

        if request.method == "POST":
            form = CardForm(request.POST)
            if form.is_valid():
                card_number = form.cleaned_data["card_number"]
                result = {
                    "valid": True,
                    "message": "✅ Карта валидна!",
                    "card_number": card_mask(card_number),
                }
            else:
                result = {
                    "valid": False,
                    "message": "❌ Карта не прошла проверку Luhn",
                }

        context = {
            "form": form,
            "result": result,
            "title": "Luhn Check",
        }
        return render(request, "admin/cards/card/luhn_check.html", context)

    @admin.display(description="Card Number")
    def formatted_card_number(self, obj):
        return card_mask(obj.card_number)

    @admin.display(description="Phone")
    def formatted_phone(self, obj):
        return phone_mask(obj.phone or "")