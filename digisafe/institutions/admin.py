from django.contrib import admin

from .models import Institution, InstitutionCustomFiles, CoursesAdmitedInstitution


class InstitutionCustomFilesInline(admin.StackedInline):
    model = InstitutionCustomFiles
    extra = 1

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
    inlines = (InstitutionCustomFilesInline, CoursesInline,)
    filter_horizontal = ("centers",)
    
    def get_queryset(self, request):
        # print("InstitutionAdmin.get_queryset")
        # path = request.path
        app_label   = request.GET.get('app_label', None)
        model_name  = request.GET.get('model_name', None)
        field_name  = request.GET.get('field_name', None)
        
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs
        # Model Protocol
        if app_label=="protocol" and model_name=="protocol" and field_name=="institution":
            # print(" qs", qs.filter(centers_=request.user.center_set.all()))
            return qs.filter(centers__director=request.user)

        return qs.filter(admin=request.user)
        