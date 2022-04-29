from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import SessionBook, DateBook


class SearchUserJobLocationForm(forms.Form):
    job = forms.CharField(label='Job', max_length=100)
    location = forms.CharField(label='Location', max_length=100)


class SessionBookForm(forms.ModelForm):
    class Meta:
        model = SessionBook
        fields = ("name", "address", "expire_date",  "start_date",  "end_date", "note")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "expire_date": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "note": forms.Textarea(attrs={"class": "form-control"}),
        }

    def clean(self):
        if self.instance:
            cleaned_data = super().clean()
            start_date = cleaned_data.get("start_date")
            end_date = cleaned_data.get("end_date")
            if end_date < start_date:
                raise ValidationError(
                    _('Data iniziale %(ds)s inferiore a quella finale %(de)s'),
                    code='invalid',
                    params={'ds': start_date, 'de': end_date, },
                )


class SessionBookUpdateForm(SessionBookForm):
    class Meta:
        model = SessionBook
        fields = ("name", "address", "note", "expire_date", "start_date", "end_date",)
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "expire_date": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "start_date": forms.DateInput(attrs={"class": "form-control bg-danger text-white", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control bg-danger text-white", "type": "date"}),
            "note": forms.Textarea(attrs={"class": "form-control"}),
        }
        help_texts = {
            'start_date': 'Attenzione. Modificando la data e salvando, si cancellano le date già registrate.',
            'end_date': 'Attenzione. Modificando la data e salvando, si cancellano le date già registrate.',
        }
