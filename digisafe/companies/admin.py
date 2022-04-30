from django.contrib import admin

from users.models import User
from .models import Company, Profile, SessionBook, DateBook


class ProfileInline(admin.StackedInline):
    model = Profile


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    inlines = (ProfileInline,)
    filter_horizontal = ("admins", "associates", "favorite",)
    search_fields = ["name", "admins__last_name", "admins__first_name"]
    list_display = ("name", "active", "list_admins", "list_favorite")
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "admins":
            kwargs["queryset"] = User.objects.filter(profile__administrator=True)
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(SessionBook)
class SessionBookAdmin(admin.ModelAdmin):
    list_display = ("id", "company", "name", "range_date", "uuid")
    filter_horizontal = ("user_option_list",)
    search_fields = ["company__name", "start_date", "end_date", "users__last_name", "users__first_name", ]


@admin.register(DateBook)
class DateBookAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "date", "users_display")
    ordering = ["date"]
    search_fields = ["session__name", "date", "users__last_name", "users__first_name", ]
    filter_horizontal = ("users",)


