from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path

from .forms import ExcelImportForm
from .models import Card
from .services import import_cards_from_excel
from .utils import card_mask, phone_mask


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
    list_filter = ("status", "expire")
    search_fields = ("card_number", "phone")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-excel/",
                self.admin_site.admin_view(self.import_excel_view),
                name="cards_card_import_excel",
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

    @admin.display(description="Card Number")
    def formatted_card_number(self, obj):
        return card_mask(obj.card_number)

    @admin.display(description="Phone")
    def formatted_phone(self, obj):
        return phone_mask(obj.phone or "")