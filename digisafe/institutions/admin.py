from django.contrib import admin
from django.db.models import Q

from protocol.models import Protocol
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
    readonly_fields = ("courses", "note")

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        if obj:
            if obj.admin == request.user:
                return []

        return super(CoursesInline, self).get_readonly_fields(request, obj)

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    search_fields = ("name", )
    ordering = ['name'] 
    inlines = (InstitutionCustomFilesInline, CoursesInline,)
    filter_horizontal = ("staff", "centers",)
    autocomplete_fields = ['admin']
    
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
        if app_label == "protocol" and model_name == "protocol" and field_name == "institution":
            # print(" qs", qs.filter(centers_=request.user.center_set.all()))
            protocol_id = request.session.get('protocol_id')
            if protocol_id:
                p = Protocol.objects.get(pk=protocol_id)
                # print(p)
                # course = p.course
                center = p.center
                return qs.filter(centers=center)
            # return qs.filter(centers__director=request.user)

        return qs.filter(Q(admin=request.user) | Q(staff=request.user) | Q(centers__trainers=request.user))


