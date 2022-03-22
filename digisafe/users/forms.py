from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.db.models import Q
from django.contrib.auth.validators import UnicodeUsernameValidator


from .models import Anagrafica, User
from countries.models import City, Country
from countries.forms import ChainedCountryForm

class UserCreationForm(UserCreationForm):
    username_validator = UnicodeUsernameValidator()
    username = forms.CharField(
        label=_('Username'),
        max_length=150,
        required=False,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    password1   = forms.CharField(label=_('Password1'), max_length=128, required=False)
    password2   = forms.CharField(label=_('Password2'), max_length=128, required=False)
    fiscal_code = forms.CharField(label=_('Fiscal code'), max_length=150, required=True)
    fiscal_code.widget.attrs.update({
        "autocomplete_check": "autocomplete_check_field",
        "autocomplete_check_model_name": "anagrafica",
        "autocomplete_check_app_label": "users",
        "autocomplete_check_field_name": "fiscal_code",
        "autocomplete": "off"
    })
    first_name  = forms.CharField(label=_('First name'), max_length=150, required=True)
    last_name   = forms.CharField(label=_('Last name'), max_length=150, required=True)
    email       = forms.EmailField(label=_('Email'), required=True)

    def __init__(self, *args, **kwargs):
        # print("UserCreationForm.__init__")
        super().__init__(*args, **kwargs)        
        
    class Meta:
        model = User
        fields = "__all__"
    
    class Media:
        js = (
            'js/autocomplete_check_fields.js',
        )
        
    def clean_fiscal_code(self):
        # print("UserCreationForm.clean_fiscal_code")
        cleaned_data = super().clean()
        fiscal_code = cleaned_data["fiscal_code"]
        # print("UserCreationForm.clean_fiscal_code", fiscal_code)
        # controlla se non esiste un altro fiscal_code in anagrafica
        check = Anagrafica.objects.filter(fiscal_code__iexact = fiscal_code)
        if check:
            raise ValidationError(
                    _('Invalid value: Fiscal code is used from other user.'),
                    code='invalid',
                )
        return fiscal_code.upper()
        
class UserForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        # print("UserForm.__init__")
        super(UserForm, self).__init__(*args, **kwargs)
        # self.fields[nome del campo].widget.attrs.update({
            # 'type': 'text',
            # 'class': 'form-control',
            # 'id': 'input-text',
        # })
        if self.instance:
            if self.fields.get("owner"):
                # Limita la lista agli utenti Anagrafica.administrator e User.superuser
                self.fields['owner'].queryset = \
                    User.objects.filter(
                                Q(profile__administrator=True) \
                                | Q(is_superuser=True)
                            ).order_by('last_name')
                    
    # def clean(self):
        # print("UserForm.clean")
        # super().clean()
        
class AnagraficaForm(ChainedCountryForm):

    class Meta:
        model = Anagrafica
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        super(AnagraficaForm, self).__init__(*args, **kwargs)
        # self.fields['fiscal_code'].required = True
        
    # def clean_fiscal_code(self):
        # print("AnagraficaForm.clean_fiscal_code")
        # if not self.cleaned_data['fiscal_code']:
            # raise ValidationError(
                    # _('Invalid value: Fiscal code can\'t empty.'),
                    # code='invalid',
                # )
            # return self.cleaned_data['fiscal_code']
        # return self.cleaned_data['fiscal_code'].upper()