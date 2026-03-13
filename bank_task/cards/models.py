from django.db import models
from django.core.validators import MinValueValidator

class CardStatus(models.TextChoices):
    ACTIVE = "active" , "Active"
    INACTIVE = "inactive" , "Inactive"
    EXPIRED = "expired" , "Expired"


class Card(models.Model):
    card_number = models.CharField(max_length=19,unique=True)
    expire = models.DateField()
    phone = models.CharField(max_length=20,blank=True,null=True)
    status = models.CharField(max_length=20,choices=CardStatus.choices,default=CardStatus.INACTIVE)
    balance = models.DecimalField(max_digits=15,decimal_places=2,validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.card_number} ({self.status})"
    