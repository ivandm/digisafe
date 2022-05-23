import json

from django.db import models
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MaxMoneyValidator, MinMoneyValidator
from djmoney.money import Money
from django.core import serializers

from users.models import User
from companies.models import SessionBook


class PriceList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    price = MoneyField(default=0.00, max_digits=7, decimal_places=2,
                       default_currency='USD', validators=[MinMoneyValidator(0), MaxMoneyValidator(99999)])
    SLOT_TIME_CHOICES = [
        ('HOUR', 'every Hour'),
        ('DAY', 'every Day'),
        ('SESSION', 'every Session'),
    ]
    slot_time = models.CharField(max_length=8, choices=SLOT_TIME_CHOICES, default="HOUR")
    note = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # print("pricelist.models.PriceList.save")
        if self.isBlock() is False:
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.isBlock() is False:
            super().delete(*args, **kwargs)

    def isBlock(self):
        # print("pricelist.models.PriceList.isBlock")
        for item in self.sessionprice_set.all():
            if item.isBlock():
                return True
        return False

    def get_total(self):
        print("pricelist.models.PriceList.get_total")
        imponibile = self.price
        currency = self.price.currency
        extra_price_list = []
        for item in self.extrapricelist_set.all():

            if item.unit == "PERC":
                item_money = item.qta / 100 * imponibile
                # print(type(item_money))
            elif item.unit == "MONEY":
                item_money = Money(item.qta, currency)
                # print(type(item_money))

            if item.add_minus == "add":
                # print("add")
                extra_price_list.append(item_money)
            elif item.add_minus == "minus":
                # print("minus")
                extra_price_list.append(-item_money)

        for extra_price in extra_price_list:
            imponibile += extra_price
        return imponibile


class ExtraPriceList(models.Model):
    pricelist = models.ForeignKey(PriceList, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    qta = models.DecimalField(max_digits=7, decimal_places=2)

    UNIT_CHOICES = [
        ('PERC', '%'),
        ('MONEY', 'Money'),
    ]
    unit = models.CharField(max_length=8, choices=UNIT_CHOICES, default="PERC")

    ADD_MINUS_CHOICES = [
        ('add', '+'),
        ('minus', '-'),
        ('incluse', 'Incluse'),
    ]
    add_minus = models.CharField(max_length=8, choices=ADD_MINUS_CHOICES, default="add")


class SessionPrice(models.Model):
    session = models.ForeignKey(SessionBook, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.ForeignKey(PriceList, on_delete=models.CASCADE, null=True, blank=True)
    price_metadata = models.JSONField(default=dict)  # future implementazioni

    def __str__(self):
        return "{} - {}".format(self.session, self.user.getFullName)

    def save(self, *args, **kwargs):
        # print("pricelist.models.SessionPrice.save")
        if not self.isBlock():
            super().save(*args, **kwargs)


    def isBlock(self):
        """
        Verifica se l'utente può aggiornare il prezzo.
        Quando l'utente è stato confermato in una sessione, non è abilitato all'aggiornamento
        :return: bool
        """
        # print("pricelist.models.SessionPrice.isBlock")
        if self.user.id in self.session.confirmed_users():
            return True
        return False
