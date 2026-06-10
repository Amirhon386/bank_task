from django import forms
from .utils import luhn_check

class ExcelImportForm(forms.Form):
    file = forms.FileField()

class CardForm(forms.Form):
    card_number = forms.CharField(max_length=19, label="Card Number")

    def clean_card_number(self):
        card_number = self.cleaned_data.get("card_number", "")
        if not luhn_check(card_number):
            raise forms.ValidationError("Invalid card number (Luhn check failed)")
        return card_number