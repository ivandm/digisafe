from django.contrib import admin

from .models import PriceList, SessionPrice, ExtraPriceList


@admin.register(SessionPrice)
class SessionPriceAdmin(admin.ModelAdmin):
    pass


class ExtraPriceInline(admin.TabularInline):
    model = ExtraPriceList
    fields = ("name", "qta", "unit", "add_minus")


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    inlines = (ExtraPriceInline, )
    autocomplete_fields = ['user', ]
    # list_display = ("id", "company", "name", "range_date", "uuid")
    # filter_horizontal = ("jobs", "user_option_list", "user_decline_list")
    # search_fields = ["company__name", "start_date", "end_date", "users__last_name", "users__first_name", ]

