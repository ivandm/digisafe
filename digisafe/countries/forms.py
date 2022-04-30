from django import forms
from django.forms import ModelForm

from countries.models import City, Country


class ChainedCountryForm(ModelForm):
    """
    Ricorda di importare lo script 'js/chained-country.js' in Media
    quando erediti la classe
    """

    class Meta:
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        # print("countries.forms.ChainedCountryForm")
        prefix = kwargs.get('prefix')
        data = kwargs.get('data')
        country_id = None
        # city_id = None
        if prefix and data:
            country_id = data.get(prefix+'-country')
            # city_id = data.get(prefix+'-city')
        super(ChainedCountryForm, self).__init__(*args, **kwargs)
        
        # se i campi non sono modificabili
        if not self.fields.get("country") and not self.fields.get("city"):
            return
            
        try:
            self.initial['country'] = kwargs['instance'].country.id
        except:
            # non esiste ancora istanza dell'oggetto
            pass
        country_list = [('', '---------')] + [(i.id, i.name) for i in Country.objects.all()]
        
        try:
            self.initial['city'] = kwargs['instance'].city.id
            city_init_form = [(i.id, i.name) for i in City.objects.filter(
                country=kwargs['instance'].country
            )]
        except:
            city_init_form = [('', '---------')]
            pass

        # Override the form, add onchange attribute to call the ajax function
        country_attrs = self.fields['city'].widget.attrs
        country_attrs.update(id="id_country")
        country_attrs.update(onchange="getCities(this)")
        self.fields['country'].widget = forms.Select(
            attrs=country_attrs,
            choices=country_list,
        )

        if country_id:
            # print("istanza non esistente")
            city_init_form = [('', '---------')]
            city_init_form_append = [
                (i.id, "%s (%s)" % (i.name, i.sigla_prov)) for i in City.objects.filter(
                    country=Country.objects.get(pk=country_id)).order_by('name')
            ]
            city_init_form = city_init_form + city_init_form_append
        elif self.initial.get('city'): #
            # print("istanza esistente")
            self.initial['city'] = kwargs['instance'].city.id
            city_init_form = [(i.id, "%s (%s)" % (i.name, i.sigla_prov)) for i in City.objects.filter(
                country=kwargs['instance'].country
            )]

        else:
            city_init_form = [('', '---------')]
            city_init_form_append = []
            if self.initial.get('country'):
                city_init_form_append = [
                        (i.id, "%s (%s)"%(i.name,i.sigla_prov)) for i in City.objects.filter(
                        country=kwargs['instance'].country).order_by('name')
                        ]
            city_init_form = city_init_form + city_init_form_append

        city_attrs = self.fields['city'].widget.attrs
        city_attrs.update(id="id_city")
        self.fields['city'].widget = forms.Select(
            attrs=city_attrs,
            choices=city_init_form
        )