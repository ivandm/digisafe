from django import forms
from djmoney.forms.widgets import MoneyWidget
from django.conf import settings
from django.forms import inlineformset_factory

from bootstrap_modal_forms.forms import BSModalModelForm

from .models import PriceList, ExtraPriceList, SessionPrice


class PriceListForm(forms.ModelForm):
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
            # 'slot_time': forms.TextInput(attrs={'class': 'form-select'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': "2"}),

        }
        help_texts = {
            "name": "Nome del profilo.",
        }


class ExtraPriceListForm(forms.ModelForm):
    class Meta:
        model = ExtraPriceList
        exclude = ["pricelist", ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'qta': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.00', 'max': "99999.99"}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'add_minus': forms.RadioSelect(attrs={'class': 'hstack gap-3'}),
        }


ExtraPriceListSet = inlineformset_factory(PriceList, ExtraPriceList,
                                          form=ExtraPriceListForm,
                                          extra=2,

                                          )


class SessionPriceForm(forms.ModelForm):
    """
    Solo gli utenti loggati avranno accesso alla loro lista di PriceList
    """
    class Meta:
        model = SessionPrice
        exclude = ('user', 'session', )

    def __init__(self, user, *args, **kwargs):
        # print("account.forms.SessionPriceForm")
        super().__init__(*args, **kwargs)
        self.fields['price'].queryset = PriceList.objects.filter(user=user)
