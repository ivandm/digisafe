from django.db import models
from djmoney.models.fields import MoneyField
from django.core.validators import MinValueValidator
from djmoney.models.validators import MaxMoneyValidator, MinMoneyValidator

from users.models import User


class PriceList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    price = MoneyField(default=0.00, max_digits=7, decimal_places=2,
                            default_currency='EUR', validators=[MinMoneyValidator(0), MaxMoneyValidator(99999)])
    SLOT_TIME_CHOICES = [
        ('HOUR', 'every Hour'),
        ('DAY', 'every Day'),
        ('SESSION', 'every Session'),
    ]
    slot_time = models.CharField(max_length=8, choices=SLOT_TIME_CHOICES, default="HOUR")

