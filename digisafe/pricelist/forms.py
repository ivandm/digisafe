from django import forms
from djmoney.forms.widgets import MoneyWidget
from django.conf import settings

from .models import PriceList


class PriceForm(forms.ModelForm):
    class Meta:
        model = PriceList
        exclude = ["user", ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': MoneyWidget(
                amount_widget=forms.TextInput(attrs={'class': 'form-class',
                                                     'placeholder': "00,00",
                                                     'aria-label': "00,00",
                                                     }),
                currency_widget=forms.Select(attrs={'class': 'form-class', },
                                             choices=settings.CURRENCY_CHOICES,
                                             ),
            ),
            'slot_time': forms.TextInput(attrs={'class': 'form-select'}),

        }
        help_texts = {
            "name": "Nome del profilo.",
        }
