from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.gis import forms as gisforms

from agenda.models import Agenda, AgendaFeatures
from users.models import User, Anagrafica
from countries.forms import ChainedCountryForm


class OSMWidget(gisforms.OSMWidget):
    # XDSoft DateTimePicker da utilizzare con il campo forms.DateTimeInput
    # https://simpleisbetterthancomplex.com/tutorial/2019/01/03/how-to-use-date-picker-with-django.html
    default_lon = 12.4963655
    default_lat = 41.9027835
    default_zoom = 8


class CalendarFormEvent(forms.ModelForm):
    class Meta:
        model = Agenda
        fields = ['city', 'date_start', 'date_end', 'object', 'description']
        widgets = {
            'city': OSMWidget(attrs={'map_width': 800, 'map_height': 500}),
            # 'anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date_start': forms.DateTimeInput(attrs={'class': 'form-control', 'id': 'datatimepicker'}),
            # 'date_start': AdminSplitDateTime(attrs={'class': 'form-control'}),
            'date_end': forms.DateTimeInput(attrs={'class': 'form-control', 'id': 'datatimepicker'}),
            'object': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

    class Media:
        # js = ('https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js')
        pass


class AccountAuthenticationForm(forms.Form):
    """
    A custom authentication form used for account.
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class AccountLoginLostForm(forms.Form):
    """
    A custom login lost request form used for account.
    """
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))


class AccountChangePasswordForm(forms.Form):
    """
    A custom change password form used for account.
    """
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label=_("Repeat password"))
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password != password2:
            raise ValidationError(
                    _("Passwords aren't the same.")
                )


class AccountResetPasswordForm(AccountChangePasswordForm):
    auth_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))


class AccountForm(forms.ModelForm):

    class Media:
        js = (
            "/static/admin/js/jquery.min.js",
            "/static/admin/js/jquery.init.js",
            'js/chained-country.js',
        )

    class Meta:
        model = User
        fields = ["email"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


class AnagraficaForm(ChainedCountryForm):

    def __init__(self, *args, **kwargs):
        # print("AnagraficaForm")
        super(AnagraficaForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Anagrafica
        fields = ["birthday", "country", "city"]
        widgets = {
            "birthday": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "country": forms.Select(attrs={"class": "form-select"}),
            "city": forms.Select(attrs={"class": "form-select"}),
        }


AnagraficaFormSet = inlineformset_factory(User, Anagrafica, form=AnagraficaForm, can_delete=False)


class AgendaFeaturesForm(forms.ModelForm):
    class Meta:
        model = AgendaFeatures
        fields = ["default_position"]

        widgets = {
            'default_position': OSMWidget(attrs={'map_width': 400, 'map_height': 400}),
        }


AgendaFeaturesFormSet = inlineformset_factory(User, AgendaFeatures, form=AgendaFeaturesForm, can_delete=False)
