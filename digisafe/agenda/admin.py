from django.contrib import admin

from django.contrib.gis import admin as gisadmin

from .models import Agenda, AgendaFeatures


@admin.register(AgendaFeatures)
class AgendaPropertyAdmin(gisadmin.OSMGeoAdmin):
    list_display = ("user", "default_position")
    search_fields = ['user']
    autocomplete_fields = ['user']


@admin.register(Agenda)
class AgendaAdmin(gisadmin.OSMGeoAdmin):
    """Marker admin."""
    list_display = ("id", "user", "jobs", "get_city_name", "busy", "date_range", "object", "date_start", "date_end")
    list_editable = ("object", "date_start", "date_end")
    search_fields = ['user__first_name', "user__last_name", "user__username"]
    autocomplete_fields = ['user', 'datebook']
