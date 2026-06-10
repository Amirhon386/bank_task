from django.urls import path
from . import views

urlpatterns = [
    path("luhn-check/", views.luhn_check_view, name="luhn_check"),
    path("import-excel/", views.import_cards, name="import_cards"),
]