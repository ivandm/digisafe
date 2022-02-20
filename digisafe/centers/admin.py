from django.contrib import admin

from .models import Center, CoursesAdmitedCenter
from .forms import CenterForm
from users.models import User

class CoursesInline(admin.StackedInline):
    model = CoursesAdmitedCenter
    can_delete = False
    show_change_link = False
    verbose_name_plural = 'Courses'
    filter_horizontal = ("courses",)
    
@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    form = CenterForm
    search_fields = ("name", )
    ordering = ['name'] 
    inlines = (CoursesInline,)
    filter_horizontal = ("trainers", "staff")
    
    def get_queryset(self, request):
        # print("CenterAdmin.get_queryset", request)
        # path = request.path
        app_label   = request.GET.get('app_label', None)
        model_name  = request.GET.get('model_name', None)
        field_name  = request.GET.get('field_name', None)
        
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs
        # Richieste dai campi autocomplete_fields
        if app_label=="protocol" and model_name=="protocol" and field_name=="center":
            # print("CenterAdmin.get_queryset qs", qs.filter(trainingcenter__user=request.user))
            return qs.filter(trainers=request.user)
            # return request.user.associate_centers.all()

        # print(qs)
        return qs.filter(director=request.user)
        # return super().get_queryset(request)
        
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        # print("CenterAdmin.get_search_results")
        return queryset, use_distinct
        
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "director":
            kwargs["queryset"] = User.objects.filter(profile__director=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "trainers":
            kwargs["queryset"] = User.objects.filter(profile__trainer=True)
        if db_field.name == "staff":
            kwargs["queryset"] = User.objects.filter(profile__director=True)
        return super().formfield_for_manytomany(db_field, request, **kwargs)