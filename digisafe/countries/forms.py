from django import forms
from django.forms import ModelForm

from countries.models import City, Country

class ChainedCountryForm(ModelForm):

    class Meta:
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        super(ChainedCountryForm, self).__init__(*args, **kwargs)
        
        # se i campi non sono modificabili
        if not self.fields.get("country") and not self.fields.get("city"):
            return
            
        try:
            self.initial['country'] = kwargs['instance'].country.id
        except:
            pass
        country_list = [('', '---------')] + [(i.id, i.name) for i in Country.objects.all()]
        
        try:
            self.initial['city'] = kwargs['instance'].city.id
            city_init_form = [(i.id, i.name) for i in City.objects.filter(
                country=kwargs['instance'].country
            )]
        except:
            city_init_form = [('', '---------')]
            
        # Override the form, add onchange attribute to call the ajax function
        self.fields['country'].widget = forms.Select(
            attrs={
                'id': 'id_country',
                'onchange': 'getCities(this)',
                # 'style': 'width:200px'
            },
            choices=country_list,
        )
        
        try:
            self.initial['city'] = kwargs['instance'].city.id
            city_init_form = [(i.id, "%s (%s)"%(i.name,i.sigla_prov)) for i in City.objects.filter(
                country=kwargs['instance'].country
            )]
            
        except:
            city_init_form = [('', '---------')]
            city_init_form_append = []
            if self.initial.get('country'):
                city_init_form_append = [
                        (i.id, "%s (%s)"%(i.name,i.sigla_prov)) for i in City.objects.filter(
                        country=kwargs['instance'].country)
                        ]
            city_init_form = city_init_form + city_init_form_append
            
        self.fields['city'].widget = forms.Select(
            attrs={
                'id': 'id_city',
                # 'onchange': 'getKecamatan(this.value)',
                # 'style': 'width:200px'
            },
            choices=city_init_form
        )