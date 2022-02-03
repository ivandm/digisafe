from django.contrib import admin

from users.models import User
from .models import Company, Profile


class ProfileInline(admin.StackedInline):
    model = Profile


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    inlines = (ProfileInline,)
    filter_horizontal = ("admins", "associates",)
    search_fields = ["name", "admins__last_name", "admins__first_name"]
    list_display = ("name", "active", "list_admins")
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "admins":
            kwargs["queryset"] = User.objects.filter(profile__administrator=True)
        return super().formfield_for_manytomany(db_field, request, **kwargs)