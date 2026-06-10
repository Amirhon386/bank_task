from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Card
from .forms import CardForm, ExcelImportForm
from .services import import_cards_from_excel
from .utils import luhn_check, card_mask

def card_list(request):
    cards = Card.objects.all()
    return render(request, "cards/card_list.html", {"cards": cards})


def luhn_check_view(request):
    result = None
    form = CardForm()

    if request.method == "POST":
        form = CardForm(request.POST)
        if form.is_valid():
            card_number = form.cleaned_data["card_number"]
            result = {
                "card_number": card_mask(card_number),
                "valid": True,
                "message": "karta validaciya qilindi"
            }
        else:
            result = {
                "valid": False,
                "message": "karta validaciya qilinmad"
            }

    return render(request, "cards/luhn_check.html", {
        "form": form,
        "result": result
    })


def import_cards(request):
    result = None
    form = ExcelImportForm()

    if request.method == "POST":
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            result = import_cards_from_excel(request.FILES["file"])

    return render(request, "cards/import_cards.html", {
        "form": form,
        "result": result
    })