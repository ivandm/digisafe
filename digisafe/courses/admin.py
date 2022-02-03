from django.contrib import admin
from .models import Courses, Feature, New, Update, ContentCourse

   
class FeatureInline(admin.StackedInline):
    model = Feature
    can_delete = False
    show_change_link = True
    verbose_name_plural = 'Features'
    filter_horizontal = ("contents",)
    
class NewInline(admin.TabularInline):
    model = New
    can_delete = False
    show_change_link = True
    verbose_name_plural = 'New'
    
class UpdateInline(admin.TabularInline):
    model = Update
    can_delete = False
    show_change_link = True
    verbose_name_plural = 'Update'
    
@admin.register(Courses)
class CourseAdmin(admin.ModelAdmin):
    inlines = (FeatureInline, NewInline, UpdateInline,)
    search_fields = ["code", "feature__title", "country__name", "country__code"]
    filter_horizontal = ("country",)
    ordering = ['-pk']
    list_display = ('feature_title', 'code', 'active', 'country_code')
    # list_editable  = ('active', 'code')

    def get_queryset(self, request):
        if not request.user.is_superuser:
            return super().get_queryset(request).filter(subjects__user=request.user)
        return super().get_queryset(request)
        

@admin.register(ContentCourse)
class ContentCourseAdmin(admin.ModelAdmin):
    search_fields = ["course__feature__title", "course__code"]
    autocomplete_fields = ['course',]
    list_display = ('__str__', 'i18',)
    ordering = ['course__feature__title', 'i18']
    list_filter = (
        "i18",
        # ("session__country", admin.RelatedOnlyFieldListFilter),
    )