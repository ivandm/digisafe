from django.contrib import admin

from .models import Institution, CoursesAdmitedInstitution

class CoursesInline(admin.StackedInline):
    model = CoursesAdmitedInstitution
    can_delete = False
    show_change_link = False
    verbose_name_plural = 'Courses'
    filter_horizontal = ("courses",)
    
@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    search_fields = ("name", )
    ordering = ['name'] 
    inlines = (CoursesInline,)
    
    def get_queryset(self, request):
        # print("InstitutionAdmin.get_queryset")
        return super().get_queryset(request)
        # todo: deve essere implementato
        path = request.path
        app_label   = request.GET.get('app_label', None)
        model_name  = request.GET.get('model_name', None)
        field_name  = request.GET.get('field_name', None)
        
        qs = super().get_queryset(request)
        
        # if path == "/admin/autocomplete/" and field_name=='owner':
            # return qs.filter(profile__administrator=1)

        # Model Protocol
        if not request.user.is_superuser and app_label=="protocol" and model_name=="protocol" and field_name=="intitution":
            print("InstitutionAdmin.get_queryset qs", qs.filter())
            return qs.filter()
            
        