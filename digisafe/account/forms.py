from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from django.contrib.admin.widgets import AdminSplitDateTime
from .models import UsersPosition


class CalendarFormEvent(forms.ModelForm):
    class Meta:
        model = UsersPosition
        fields = ['anonymous', 'date_start', 'date_end', 'object', 'description']
        widgets = {
            'anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date_start': forms.DateTimeInput(attrs={'class': 'form-control'}),
            # 'date_start': AdminSplitDateTime(),
            'date_end': forms.DateTimeInput(attrs={'class': 'form-control'}),
            'object': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

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
    password  = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label=_("Repeat passord"))
    
    def clean(self):
        cleaned_data = super().clean()
        password  = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password != password2:
            raise ValidationError(
                    _("Passwords aren't the same.")
                )

class AccountResetPasswordForm(AccountChangePasswordForm):
    auth_code  = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))