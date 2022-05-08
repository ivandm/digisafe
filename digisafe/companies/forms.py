from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.forms.models import inlineformset_factory
from django.core.validators import MinValueValidator
from django.utils.safestring import mark_safe

from .models import SessionBook, DateBook, Company, Profile
from countries.forms import ChainedCountryForm


class SearchUserJobLocationForm(forms.Form):
    job = forms.CharField(label='Job', max_length=100)
    location = forms.CharField(label='Location', max_length=100)


class SessionBookForm(forms.ModelForm):
    class Meta:
        model = SessionBook
        fields = ("name", "address", "expire_date",  "start_date",  "end_date", "jobs", "note")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "expire_date": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "note": forms.Textarea(attrs={"class": "form-control clearfix"}),
        }

    class Media:
        js = (
            '/admin/jsi18n/',
            '/static/admin/js/core.js',
            '/static/admin/js/SelectFilter2.js',
            '/static/admin/js/SelectBox.js',
        )
        css = {
            'all': (
                '/static/admin/css/forms.css',
            ),
        }

    def clean(self):
        if self.instance:
            cleaned_data = super().clean()
            exp_date = cleaned_data.get("expire_date")
            start_date = cleaned_data.get("start_date")
            end_date = cleaned_data.get("end_date")
            if end_date < start_date:
                raise forms.ValidationError(
                    _('Data iniziale %(ds)s inferiore a quella finale %(de)s'),
                    code='invalid',
                    params={'ds': start_date, 'de': end_date, },
                )
            if exp_date.date() > start_date:
                raise forms.ValidationError(
                    _('Data di scadenza %(lab_ed)s %(ed)s '
                      'dovrebbe essere antecedente o uguale a quella di inizio %(ds)s'
                      ),
                    code='invalid',
                    params={'ds': start_date,
                            'ed': exp_date.date(),
                            'lab_ed': self.fields['expire_date'].label},
                )


class SessionBookUpdateForm(SessionBookForm):
    class Meta:
        model = SessionBook
        fields = ("name", "address", "expire_date", "start_date", "end_date", "jobs", "note")
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
            'jobs': 'Attenzione. Eliminando una scelta si cancellano i dati già inseriti.',
        }


class DateBookForm(forms.ModelForm):
    min_number_user = 0  # numero minimo nel campo type="number"
    number_user = forms.IntegerField(validators=[MinValueValidator(min_number_user)])

    class Meta:
        model = DateBook
        fields = ("job", "date", "number_user")
        # fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["job"].disabled = True
        self.fields["date"].disabled = True
        # Or to set READONLY
        # self.fields["job"].widget.attrs["readonly"] = True
        self.fields["job"].widget.attrs["class"] = "bg-secondary text-white"
        # self.fields["date"].widget.attrs["readonly"] = True
        self.fields["date"].widget.attrs["class"] = "bg-secondary text-white"
        self.fields["number_user"].widget.attrs["min"] = "{}".format(self.min_number_user)


DateBookFormSet = inlineformset_factory(SessionBook, DateBook, form=DateBookForm,
                                        fk_name='session',
                                        can_delete=False,
                                        extra=0,
                                        )


class SettingsForm(forms.ModelForm):

    class Media:
        js = (
            "/static/admin/js/jquery.min.js",
            "/static/admin/js/jquery.init.js",
            'js/chained-country.js',
        )

    class Meta:
        model = Company
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
        }


class ProfileForm(ChainedCountryForm):

    class Meta:
        model = Profile
        fields = ["country", "city", "desc", "logo"]
        widgets = {
            "country": forms.Select(attrs={"class": "form-select"}),
            "city": forms.Select(attrs={"class": "form-select"}),
            "desc": forms.Textarea(attrs={"class": "form-control"}),
        }


ProfileFormSet = inlineformset_factory(Company, Profile, form=ProfileForm, can_delete=False)
