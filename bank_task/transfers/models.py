from django.db import models
from cards.models import Card


class Transfer(models.Model):
    class State(models.TextChoices):
        CREATED = "created", "Created"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    ext_id = models.CharField(max_length=100, unique=True)
    sender_card_number = models.CharField(max_length=19)
    receiver_card_number = models.CharField(max_length=19)
    sender_card_expiry = models.DateField()
    sender_phone = models.CharField(max_length=20, blank=True, null=True)
    receiver_phone = models.CharField(max_length=20, blank=True, null=True)
    sending_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.IntegerField()
    receiving_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    state = models.CharField(max_length=20, choices=State.choices, default=State.CREATED)
    try_count = models.IntegerField(default=0)
    otp = models.CharField(max_length=6, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ext_id} ({self.state})"


class Error(models.Model):
    code = models.IntegerField(unique=True)
    en = models.CharField(max_length=255)
    ru = models.CharField(max_length=255)
    uz = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.code}: {self.en}"