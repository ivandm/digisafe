from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.crypto import get_random_string
from django.utils.translation import ngettext, gettext as _
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist

from django.contrib import messages
from leaflet.admin import LeafletGeoAdmin

from account.models import UsersPosition
from .models import User, Anagrafica, Profile, Subjects, Institutions
from .forms import AnagraficaForm, UserForm, UserCreationForm

    
# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class AnagraficaInline(admin.StackedInline):
    model = Anagrafica
    form = AnagraficaForm
    can_delete = False
    show_change_link = True
    verbose_name_plural = 'Anagrafiche'
    autocomplete_check_fields = ['fiscal_code']
    add_fieldsets = (
        (None, {
            # 'classes': ('wide',),
            'fields': ('fiscal_code',)}
        ),
    )
    class Media:
        js = (
            'js/chained-country.js',
            'js/autocomplete_check_fields.js',
        )
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """aggiunge la gli attributi ai campi della lista autocomplete_check_fields """
        # print("formfield_for_dbfield", db_field)
        if not hasattr(self, "autocomplete_check_fields"):
            self.autocomplete_check_fields = []
        if 'widget' not in kwargs:
            if db_field.name in self.autocomplete_check_fields:
                widget = db_field.formfield().widget
                attr = widget.attrs.update({
                    "autocomplete_check":"autocomplete_check_field",
                    "autocomplete_check_model_name":self.model.__name__.lower(),
                    "autocomplete_check_app_label":self.model._meta.app_label.lower(),
                    "autocomplete_check_field_name":db_field.name,
                    "autocomplete":"off"
                    })
                # print(attr)
                kwargs['widget'] = widget
        return super().formfield_for_dbfield(db_field, request, **kwargs)
        
    def get_fieldsets(self, request, obj=None):
        # print("AnagraficaInline.get_fieldsets", obj)
        return super().get_fieldsets(request, obj)
        if obj is None:
            return self.add_fieldsets
        else:
            return super().get_fieldsets(request, obj)
                    
# which acts a bit like a singleton
class ProfileInline(admin.TabularInline):
    model = Profile
    can_delete = False
    show_change_link = False
    verbose_name_plural = 'Profile'
    
class SubjectsInline(admin.StackedInline):
    model = Subjects
    can_delete = False
    show_change_link = False
    verbose_name_plural = 'Subjects'
    filter_horizontal = ("subjects",)


class InstitutionsInLine(admin.StackedInline):
    model = Institutions
    can_delete = False
    show_change_link = False
    verbose_name_plural = 'Institutions Centers'
    filter_horizontal = ("institutions",)
    
# Define a new User admin
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserForm
    # model = User
    inlines_superuser = (AnagraficaInline, ProfileInline, SubjectsInline, InstitutionsInLine)
    inlines = (AnagraficaInline,)
    ordering = ['-pk']
    list_per_page = 20
    search_fields = ["username", "last_name", "first_name", "anagrafica__fiscal_code", "trainingcenter__centers__name"]
    autocomplete_fields = ['owner',]
    # filter_horizontal = BaseUserAdmin.filter_horizontal + ("subjects",)
    fieldsets = (
        *BaseUserAdmin.fieldsets,  # original form fieldsets, expandeds follows
        (                      
            'Custom Fields',  # Gruppo campi personalizzati
            {
                'fields': (
                    'description',
                    'owner',
                ),
                
            },
        ),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # 'fields': ('username', 'password1', 'password2', 'first_name', 'last_name')
            'fields': ('first_name', 'last_name', 'fiscal_code')
            }
        ),
    )
    list_filter = (
        "is_superuser",
        "is_staff",
        "profile__director",
        "profile__trainer",
        "profile__administrator",
    )
    list_editable = ("is_staff",)
    actions = ['make_trainer','make_director','make_administrator','make_institution','make_log',]
    # prepopulated_fields = {"username": ("first_name", "last_name")}
    
    class Media:
        js = (
            'js/autocomplete_check_fields.js',
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get_list_display(self, request):
        if not request.user.is_superuser:
            list_display = (
                "username",
                "email",
                "last_name",
                "first_name",
                "fiscal_code",
            )
            return list_display
        return (
                "username",
                "email",
                "last_name",
                "first_name",
                "fiscal_code",
                "is_staff"
            )
            
    def get_list_filter(self, request):
        if request.user.is_superuser:
            list_filter = (
                "is_superuser",
                "is_staff",
                "profile__director",
                "profile__trainer",
                "profile__administrator",
            )
            return list_filter
        return []
    
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return (
                    "owner", 
                    "groups", 
                    "user_permissions",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "last_login",
                    "date_joined",
                    )
        return []
        
    def get_inline_instances(self, request, obj=None):
        # print("UserAdmin.get_inline_instances", obj)
        if obj is None:
            return []
        if request.user.is_superuser:
            return [inline(self.model, self.admin_site) for inline in self.inlines_superuser]
        return [inline(self.model, self.admin_site) for inline in self.inlines]
        
    def save_model(self, request, obj, form, change):
        # print("UserAdmin.save_model change", change) 
        # print("UserAdmin.save_model form", form.is_valid())
        # return super().save_model(request, obj, form, change)
        if getattr(obj, 'owner', None) is None and form.is_valid() and not change: #solo alla creazione del record
            # print("save_model", request.user)
            obj.owner = request.user
            first_name = form.cleaned_data['first_name']
            last_name  = form.cleaned_data['last_name']
            username = "{first_name}.{last_name}".format(
                                                        first_name=first_name, 
                                                        last_name =last_name
                                                   ).lower()
            username_temp = username
            i = 1
            while(User.objects.filter(username__iexact=username_temp)):
                username_temp = username + str(i)
                # print("while", username)
                i += 1
            obj.username = username_temp
            password = get_random_string(length=12)
            obj.set_password(password)
            # print("UserAdmin.save_model password", password)
            obj.save()
            # print("fiscal_code: ", form.cleaned_data['fiscal_code'])
            a=Anagrafica(fiscal_code=form.cleaned_data['fiscal_code'],user=obj)
            a.save()
        else:
            # print("UserAdmin.save_model else")
            super().save_model(request, obj, form, change)
        
    def get_form(self, request, obj=None, **kwargs):
        # print("UserAdmin.get_form", type(obj), kwargs)
        return super().get_form(request, obj, **kwargs)
        
    def get_queryset(self, request):
        # print("UserAdmin.get_queryset")
        path = request.path
        app_label   = request.GET.get('app_label', None)
        model_name  = request.GET.get('model_name', None)
        field_name  = request.GET.get('field_name', None)
        
        qs = super().get_queryset(request)
        
        # if path == "/admin/autocomplete/" and field_name=='owner':
            # return qs.filter(profile__administrator=1)
        # Model User
        if not request.user.is_superuser and app_label=="users" and model_name=="user" and field_name=="owner":
            return qs.filter(owner=request.user)
        # Model Learners
        elif "not request.user.is_superuser" and app_label=="protocol" and model_name=="learners" and field_name=="user":
            return qs.order_by("last_name")
        # Model Session
        elif "not request.user.is_superuser" and app_label=="protocol" and model_name=="session" and field_name=="trainer":
            return qs.filter(profile__trainer=1).order_by("last_name")
        # Others not superuser return only owner's users
        elif not request.user.is_superuser:
            return qs.filter(owner=request.user)
            
        return super().get_queryset(request)

    def get_actions(self, request):
        #solo il super utente (e forse qualcun altro) ha i permessi per le azioni, pertanto ha senso che le veda
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            self.actions = []
            # del actions['make_trainer']
        return actions

    # Actions
    @admin.action(description='Mark trainer')
    def make_trainer(self, request, queryset):
        for q in queryset:
            # print("q: ", q, "q.profile.trainer" ,q.profile.trainer)
            q.profile.trainer = True
            q.profile.save()
            # print("q: ", q, "q.profile.trainer" ,q.profile.trainer)
            group = Group.objects.get(name='Trainer')
            q.groups.add(group)
            self.message_user(request, _(
                    '%s is a Trainer now',
                ) % q, messages.SUCCESS)
                # queryset.update(trainer=True)
    
    @admin.action(description='Mark director')
    def make_director(self, request, queryset):
        for q in queryset:
            q.profile.director = True
            q.profile.save()
            group = Group.objects.get(name='Director')
            q.groups.add(group)
            self.message_user(request, _(
                    '%s is a director now',
                ) % q, messages.SUCCESS)
                # queryset.update(trainer=True)
    
    @admin.action(description='Mark administrator')
    def make_administrator(self, request, queryset):
        for q in queryset:
            q.profile.administrator = True
            q.profile.save()
            group = Group.objects.get(name='Administrator')
            q.groups.add(group)
            self.message_user(request, _(
                    '%s is an administrator now',
                ) % q, messages.SUCCESS)
                # queryset.update(trainer=True)
    
    @admin.action(description='Mark institution')
    def make_institution(self, request, queryset):
        for q in queryset:
            try:
                q.profile.institution = True
            except ObjectDoesNotExist:
                p = Profile(user=q)
                p.save()
                q.profile.institution = True
            q.profile.save()    
            group = Group.objects.get(name='Institution')
            q.groups.add(group)
            self.message_user(request, _(
                            '%s is an institution now',
                        ) % q, messages.SUCCESS)
                        # queryset.update(trainer=True)
    
    @admin.action(description='Mark log')
    def make_log(self, request, queryset):
        #update = queryset.update(is_log=True)
        for q in queryset:
            group = Group.objects.get(name='Log')
            q.groups.add(group)
        self.message_user(request, _(
            '%d user is log now',
            ) % update, messages.SUCCESS)
            # queryset.update(trainer=True)
    
    
# Register Custom UserAdmin
admin.site.register(User, UserAdmin)

#Position
admin.site.register(UsersPosition, LeafletGeoAdmin)



