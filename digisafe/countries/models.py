from django.db import models
from django.utils.translation import gettext as _

#stati del mondo
class Country(models.Model):
    name = models.CharField(max_length=255, default='')
    code = models.CharField(max_length=2, default='')
    
    class Meta:
        verbose_name_plural = _("countries")
        ordering = ['name']
        
    def __str__(self):
        return "{name} ({code})".format(name=self.name, code=self.code)
    
# comuni
class City(models.Model):
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        null = True,
    )
    name = models.CharField(max_length=255, default='')
    prov = models.CharField(max_length=255, default='')
    sigla_prov = models.CharField(max_length=10, default='')
    
    class Meta:
        verbose_name_plural = _("cities")
        
    def __str__(self):
        return "{name} ({prov}) [{country}]".format(name=self.name, prov=self.sigla_prov, country=self.country.code)
   
