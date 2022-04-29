from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Country, City


@login_required
def city_list(request, country_id):
    cities = City.objects.filter(country=country_id).order_by('name')
    return JsonResponse({'data': [{'id': p.id, 'name': p.name, 'prov': p.sigla_prov} for p in cities]})
