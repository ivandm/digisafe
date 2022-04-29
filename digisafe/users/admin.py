from django.contrib import admin
from django.contrib.gis.forms.widgets import OSMWidget
from django.contrib.gis.db import models as gismodel
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as _
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from django.conf import settings

from protocol.models import Protocol
from agenda.models import AgendaFeatures
from .models import User, Anagrafica, Profile, JobProfile, Subjects, Institutions
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
            'fields': ('fiscal_code',)
        }),
    )

    class Media:
        js = (
            'js/chained-country.js',
            'js/autocomplete_check_fields.js',
        )
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """ Aggiunge gli attributi ai campi della lista autocomplete_check_fields """
        # print("formfield_for_dbfield", db_field)
        if not hasattr(self, "autocomplete_check_fields"):
            self.autocomplete_check_fields = []
        if 'widget' not in kwargs:
            if db_field.name in self.autocomplete_check_fields:
                widget = db_field.formfield().widget
                # attr = widget.attrs.update({
                #     "autocomplete_check": "autocomplete_check_field",
                #     "autocomplete_check_model_name": self.model.__name__.lower(),
                #     "autocomplete_check_app_label": self.model._meta.app_label.lower(),
                #     "autocomplete_check_field_name": db_field.name,
                #     "autocomplete": "off"
                #     })
                # print(attr)
                kwargs['widget'] = widget
        return super().formfield_for_dbfield(db_field, request, **kwargs)
        
    def get_fieldsets(self, request, obj=None):
        # print("AnagraficaInline.get_fieldsets", obj)
        return super().get_fieldsets(request, obj)
        # if obj is None:
        #     return self.add_fieldsets
        # else:
        #     return super().get_fieldsets(request, obj)
        pass
                    

class ProfileInline(admin.TabularInline):
    model = Profile
    can_delete = False
    show_change_link = False
    verbose_name_plural = 'Profile'


class AgendaPropertyInline(admin.TabularInline):
    model = AgendaFeatures
    can_delete = False
    show_change_link = False
    verbose_name_plural = 'Jobs'
    filter_horizontal = ("job",)
    formfield_overrides = {
        gismodel.PointField: {"widget": OSMWidget},
    }


class JobProfileInline(admin.TabularInline):
    model = JobProfile
    can_delete = False
    show_change_link = False
    verbose_name_plural = 'Jobs'
    filter_horizontal = ("job",)


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
    inlines_superuser = (AnagraficaInline, ProfileInline, AgendaPropertyInline,
                         JobProfileInline, SubjectsInline, InstitutionsInLine)
    inlines = (AnagraficaInline,)
    ordering = ['-pk']
    list_per_page = 20
    search_fields = ["username", "last_name", "first_name", "anagrafica__fiscal_code",
                     "associate_centers__name", "center__name"]
    autocomplete_fields = ['owner']
    # filter_horizontal = BaseUserAdmin.filter_horizontal + ("subjects",)
    fieldsets = (
        *BaseUserAdmin.fieldsets,  # original form fieldsets, expand follows
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
            'fields': ('fiscal_code', 'first_name', 'last_name', 'email')
         }),
    )
    list_filter = (
        "is_superuser",
        "is_staff",
        "profile__director",
        "profile__trainer",
        "profile__administrator",
    )
    list_editable = ("is_staff",)
    actions = ['make_trainer', 'make_director', 'make_administrator', 'make_institution', 'make_log']
    # prepopulated_fields = {"username": ("first_name", "last_name")}
    
    class Media:
        js = (
            'js/autocomplete_check_fields.js',
        )
        css = {
            'all': (
                "/static/css/site.css",
            )
        }
    
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
        print("UserAdmin.save_model")
        # print("UserAdmin.save_model form", form.is_valid())
        # return super().save_model(request, obj, form, change)
        # Quando viene creato un nuovo utente
        if getattr(obj, 'owner', None) is None and form.is_valid() and not change:
            # print("save_model", request.user)
            obj.owner = request.user
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = "{first_name}.{last_name}".format(
                                                        first_name=first_name, 
                                                        last_name=last_name
                                                   ).lower()
            username_temp = username
            i = 1
            while User.objects.filter(username__iexact=username_temp):
                username_temp = username + str(i)
                # print("while", username)
                i += 1
            obj.username = username_temp
            password = get_random_string(length=12)
            obj.set_password(password)
            obj.save()
            a = Anagrafica(fiscal_code=form.cleaned_data['fiscal_code'], user=obj)
            a.save()
            # print("user: ", obj)
            # print("password: ", password)
            # print("fiscal_code: ", form.cleaned_data['fiscal_code'])
            self.send_email_new_user(obj, password)

        # quando viene modificato un utente
        else:
            # print("UserAdmin.save_model else")
            super().save_model(request, obj, form, change)
        
    def get_form(self, request, obj=None, **kwargs):
        # print("UserAdmin.get_form", type(obj), kwargs)
        return super().get_form(request, obj, **kwargs)
        
    def get_queryset(self, request):
        # print("UserAdmin.get_queryset")
        # path = request.path
        app_label = request.GET.get('app_label', None)
        model_name = request.GET.get('model_name', None)
        field_name = request.GET.get('field_name', None)
        
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs
        
        # if path == "/admin/autocomplete/" and field_name=='owner':
            # return qs.filter(profile__administrator=1)
        # Model User
        if not request.user.is_superuser and app_label == "users" and model_name == "user" and field_name == "owner":
            return qs.filter(owner=request.user)

        # Model Learners
        elif app_label == "protocol" and model_name == "learners" and field_name == "user":
            return qs.order_by("last_name")

        # Model Session
        elif app_label == "protocol" and model_name == "session" and field_name == "trainer":
            protocol_id = request.session.get('protocol_id')
            if protocol_id:
                p = Protocol.objects.get(pk=protocol_id)
                course = p.course
                center = p.center
                # print(course)
                # print(center)
                return qs.filter(
                    is_active=True, profile__trainer=1,
                    materie__subjects=course, associate_centers=center).exclude(
                    Q(associate_centers=None) | Q(materie__subjects=None)).order_by("last_name")
            else:
                return qs.none()  # return empty query

        # Model request: Institution. Restituisce utenti con profilo institution=True
        elif app_label == "institutions" and model_name == "institution" and field_name == "admin":
            return qs.filter(profile__institution=True)

        # Others not superuser return only owner's users
        # print(request.user.associate_staff.all())
        # | Q(associate_staff=request.user)
        return qs.filter(Q(owner=request.user))

    def get_actions(self, request):
        # solo il super utente (e forse qualcun altro) ha i permessi per le azioni, pertanto ha senso che le veda
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
        # todo: `update` era commentato ma non saprei perché, utilizzato dopo in self.message_user
        update = queryset.update(is_log=True)
        for q in queryset:
            group = Group.objects.get(name='Log')
            q.groups.add(group)
        self.message_user(request, _(
            '%d user is log now',
            ) % update, messages.SUCCESS)
        # queryset.update(trainer=True)
    
    def send_email_new_user(self, user, password):
        msg = _("Dear,:\n {name} {surname}".format(name=user.first_name, surname=user.last_name, ))
        msg += "\n\n"
        msg += _("Username: {}".format(user.username))
        msg += "\n"
        msg += _("Password: {}".format(password))
        msg += "\n\n"
        current_site = settings.CURRENT_SITE
        http = settings.HTTP
        msg += _("Link to login: {}{}".format(http+current_site, reverse("account:login")))
        subject = _("Create new account")
        user.sendSystemEmail(subject, msg)


# Register Custom UserAdmin
admin.site.register(User, UserAdmin)
