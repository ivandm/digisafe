from django.contrib import admin

from .models import Country, City

class CountryAdmin(admin.ModelAdmin):
    search_fields = ['name','code',]
    ordering = ['name']
    
admin.site.register(Country, CountryAdmin)

class CityAdmin(admin.ModelAdmin):
    search_fields = ['name']
    ordering = ['name']
    
admin.site.register(City, CityAdmin)