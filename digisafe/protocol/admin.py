from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import gettext as _
from django.db.models import Q
from django.template.response import TemplateResponse
from django.conf import settings

from utils import time
from utils.helper import *
from datetime import timedelta
import numpy
from itertools import chain

from .models import Protocol, Session, Learners, Files, Authorizations, Action
from .forms import ProtocolForm, SessionForm, LearnersForm, FilesForm
from courses.models import Courses
from users.models import User
from .forms import DeniedConfirmForm, IntegrationInfoForm

# class manage status
class StatusManager:
    status_form = ""
    def _set_status_form(self, request, obj, **kwargs):
        if obj:
            status  = obj.status
            default = "_set_status_form_default"
            method = "_set_%s_status_form"%status
            # print("method", method)
            if hasattr(self, method):
                return getattr(self, method)(request, obj, **kwargs)
            elif hasattr(self, default):
                return getattr(self, default)(request, obj, **kwargs)
        else:
            # niente oggetto = nuovo protocollo
            return self._set_status_form_add(request, obj, **kwargs)
            
    def _set_status_form_add(self, request, obj, **kwargs):
        # print("StatusManager._set_status_form_add", kwargs)
        return kwargs
        
    def _set_status_form_default(self, request, obj, **kwargs):
        # print("_set_status_form_default", request, obj, kwargs)
        # self.readonly_fields = self.readonly_fields + ("course", "type")
        return kwargs
        
    def _set_m_status_form(self, request, obj, **kwargs):
        # print("set_m_status_form", request, obj, kwargs)
        return self._set_status_form_default(request, obj, **kwargs)
            
    def _set_r_status_form(self, request, obj, **kwargs):
        # print("set_c_status_form", request, obj, kwargs)
        self._set_status_form_default(request, obj, **kwargs)
            
    def _set_c_status_form(self, request, obj, **kwargs):
        # print("set_r_status_form", request, obj, kwargs)
        return self._set_status_form_default(request, obj, **kwargs)
            
    def _set_a_status_form(self, request, obj, **kwargs):
        # print("set_a_status_form", request, obj, kwargs)
        return self._set_status_form_default(request, obj, **kwargs)
            
    def _set_n_status_form(self, request, obj, **kwargs):
        # print("set_n_status_form", request, obj, kwargs)
        return self._set_status_form_default(request, obj, **kwargs)
        
    def _set_t_status_form(self, request, obj, **kwargs):
        # print("set_t_status_form", request, obj, kwargs)
        return self._set_status_form_default(request, obj, **kwargs)
            
    def _set_h_status_form(self, request, obj, **kwargs):
        # print("set_h_status_form", request, obj, kwargs)
        return self._set_status_form_default(request, obj, **kwargs)
            
    def _set_status_change_view(self, request, object_id, form_url, extra_context):
        if object_id:
            status = Protocol.objects.get(pk=object_id).status
            default = "_set_status_change_view_default"
            method = "_set_%s_status_change_view"%status
            if hasattr(self, method):
                return getattr(self, method)(request, object_id, form_url, extra_context)
            elif hasattr(self, default):
                return getattr(self, default)(request, object_id, form_url, extra_context)
    
    def _set_status_change_view_default(self, request, object_id, form_url, extra_context):
        if extra_context is None:
                extra_context = {}
        return extra_context
        
    def _set_m_status_change_view(self, request, object_id, form_url, extra_context):
        if self._has_perm_m_status(request):
            if extra_context is None:
                extra_context = {}
            extra_context["show_richiesta"] = extra_context["show_insert"] = True
        return extra_context
        
    def _set_r_status_change_view(self, request, object_id, form_url, extra_context):
        if self._has_perm_m_status(request):
            if extra_context is None:
                extra_context = {}
            extra_context["show_carica"] = True
        return extra_context
        
    def _set_c_status_change_view(self, request, object_id, form_url, extra_context):
        if self._has_perm_m_status(request):
            if extra_context is None:
                extra_context = {}
            extra_context["show_autorizza"] = True
            extra_context["show_nega"] = True
        return extra_context
        
    def _set_a_status_change_view(self, request, object_id, form_url, extra_context):
        if self._has_perm_m_status(request):
            if extra_context is None:
                extra_context = {}
            extra_context["show_termina"] = True
        return extra_context
        
    def _set_n_status_change_view(self, request, object_id, form_url, extra_context):
        if self._has_perm_m_status(request):
            if extra_context is None:
                extra_context = {}
            # extra_context["show_termina"] = True
        return extra_context
        
    def _set_t_status_change_view(self, request, object_id, form_url, extra_context):
        if self._has_perm_m_status(request):
            if extra_context is None:
                extra_context = {}
            extra_context["show_chiudi"] = True
        return extra_context
        
    def _set_h_status_change_view(self, request, object_id, form_url, extra_context):
        if self._has_perm_m_status(request):
            if extra_context is None:
                extra_context = {}
            # extra_context["show_chiudi"] = True
        return extra_context
        
    def _set_status_response_change(self, request, obj):
        if obj:
            status  = obj.status
            default = "_set_status_response_change_default"
            method = "_set_%s_status_response_change"%status
            # print("method", method)
            if hasattr(self, method):
                return getattr(self, method)(request, obj)
            elif hasattr(self, default):
                return getattr(self, default)(request, obj)
    
    def _set_status_response_change_default(self, request, obj):
        pass       
    
    def _has_perm_m_status(self, request):
        return request.user.profile.trainer or not request.user.is_superuser
    def _has_perm_r_status(self, request):
        return request.user.profile.administrator or not request.user.is_superuser
    def _has_perm_c_status(self, request):
        return request.user.profile.institution or not request.user.is_superuser
    def _has_perm_a_status(self, request):
        return request.user.profile.trainer or not request.user.is_superuser
    def _has_perm_n_status(self, request):
        return request.user.profile.institution or not request.user.is_superuser
    def _has_perm_t_status(self, request):
        return request.user.profile.institution or not request.user.is_superuser
    def _has_perm_h_status(self, request):
        return request.user.profile.institution or not request.user.is_superuser
    

class SessionInline(admin.TabularInline, StatusManager):
    model = Session
    form = SessionForm
    template = "admin/edit_inline/tabular_trainer.html"
    can_delete = True
    show_change_link = True
    verbose_name_plural = 'Sessions'
    ordering = ("date", "start_time" )
    extra = 0
    autocomplete_fields = ['trainer']
    # search_fields = ['trainer']
    readonly_fields_not_modify = ("trainer", "subject_type", "execution", "country", "city", "address", "date", "start_time", "end_time")
    # readonly_fields_not_modify = ()

    
    class Media:
        css = {
            'all': (
                'css/digisafe.css',
            )}
        js = (
            'js/chained-country.js',
            # 'js/ascolumns.js',
        )
    
    def get_max_num(self, request, obj=None, **kwargs):
        # print("LearnersInline.get_max_num", obj)
        if obj:
            if obj.status != 'm' or obj.owner != request.user: return 0
        
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return super().get_readonly_fields(request, obj)
        if obj:
            if obj.status != 'm' or obj.owner != request.user:
                self.can_delete = False
                return self.readonly_fields_not_modify
        return super().get_readonly_fields(request, obj)
    
    def get_search_results(self, request, queryset, search_term):
        # print("SessionInline.get_search_results")
        return super().get_search_results(request, queryset, search_term)
        

class LearnersInline(admin.TabularInline, StatusManager):
    model = Learners
    form = LearnersForm
    template = "admin/edit_inline/tabular_learner.html"
    can_delete = True
    show_change_link = False
    verbose_name_plural = 'Learners'
    extra = 0
    autocomplete_fields = ['user']
    readonly_fields_all = ["user", "passed", "inst_cert"]
            
    def get_fields(self, request, obj=None):
        if obj:
            if obj.course.need_institution:
                if obj.status in ["t"] and request.user.profile.institution  and obj.checkAllSignedFiles():
                    return ('user', 'passed', 'inst_cert')
                if obj.status in ["h"]:
                    return  ('user', 'passed', 'inst_cert')
        return  ('user', 'passed')
        
    def get_max_num(self, request, obj=None, **kwargs):
        # print("LearnersInline.get_max_num", obj)
        
        if obj:
            max_learner = obj.learners_request
            if request.user.is_superuser:
                return int(max_learner)
            if (obj.status == 'm' or obj.status == 'a') and obj.owner == request.user :
                type = obj.type
                # max_learner_theory = getattr(obj.course, type).max_learners_theory
                return int(max_learner)
            else:
                return 0
    
    def get_readonly_fields(self, request, obj=None):
        # print("LearnersInline.get_readonly_fields")
        if request.user.is_superuser:
            return []
        if obj:
            fields = []
            status = obj.status
            if request.user.profile.institution and status in ["t"]:
                fields = ['user', 'passed']
            elif status not in ["m", "a"]:
                # print("LearnersInline.get_readonly_fields m")
                fields = self.readonly_fields_all
            elif status == 'a' and obj.owner == request.user:
                # print("LearnersInline.get_readonly_fields a")
                fields = ["inst_cert"]
            return fields
        return super().get_readonly_fields(request, obj)
        
    def get_formset(self, request, obj=None, **kwargs):
        # print("LearnersInline.get_formset")
        # print("request", request)
        # self.readonly_fields = ()
        # self._set_status_form(request, obj, **kwargs)
        if obj:
            if request.user.is_superuser:
                self.can_delete = True
            elif (obj.status == 'm' or obj.status == 'a') and obj.owner == request.user :
                # print("LearnersInline.get_formset m and a")
                self.can_delete = True
            else:
                # print("LearnersInline.get_formset others")
                self.can_delete = False
            if obj.status in ["t"] and not obj.checkAllSignedFiles():
                for c in obj.files_set.all():
                    if not c.check_signed():
                        messages.add_message(request, messages.WARNING, _('{0} File documentation have not been signed yet.'.format(c.get_doc_type_display())))
                
        return super().get_formset(request, obj, **kwargs)

    def get_ordering(self, request):
        return ['pk']

class FilesInline(admin.TabularInline, StatusManager):
    model = Files
    # form = FilesForm
    template = "admin/edit_inline/tabular_files.html"
    can_delete = True
    show_change_link = False
    verbose_name_plural = 'Files'
    extra = 1
    # autocomplete_fields = ['user']
    readonly_fields_not_modify = ["datetime", "doc_type", "file"]
    
    class Media:
        js = (
            "/static/js/filesinline.js",
        )
        
    def get_max_num(self, request, obj=None, **kwargs):
        # print("FilesInline.get_max_num", obj)
        if obj:
            if obj.owner == request.user and obj.status == 'a':
                # Documenti dell'Ente
                if obj.course.need_institution and obj.institution.use_custom_files:
                    return obj.institution.institutioncustomfiles_set.count()
                # Documenti IRCoT
                return len(self.model.doc_type.field.choices)
            else:
                return 0
        return 0
        
    def get_readonly_fields(self, request, obj=None):
        # print("FilesInline.get_readonly_fields")
        if obj:
            status = obj.status
            if obj.owner == request.user and status == 'a':
                # print("FilesInline.get_readonly_fields not modify")
                return []
            else:
                # print("FilesInline.get_readonly_fields modify")
                return self.readonly_fields_not_modify
        return super().get_readonly_fields(request, obj)
    
    def get_formset(self, request, obj=None, **kwargs):
        # print("FilesInline.get_formset kwargs", kwargs)
        # self.readonly_fields = ()
        # self._set_status_form(request, obj, **kwargs)
        self.obj = obj
        if obj:
            if obj.owner == request.user and obj.status == 'a':
                # print("FilesInline.get_readonly_fields not modify")
                self.can_delete = True
            else:
                # print("FilesInline.get_readonly_fields modify")
                self.can_delete = False
        return super().get_formset(request, obj, **kwargs)
    
        
class AuthorizationsInline(admin.TabularInline, StatusManager):
    model = Authorizations
    # form = FilesForm
    can_delete = True
    show_change_link = False
    verbose_name_plural = 'Authorizations'
    extra = 1
    # autocomplete_fields = ['user']
    readonly_fields_not_modify = ["auth_prot", "datetime", "doc_type", "file"]
    
    def get_max_num(self, request, obj=None, **kwargs):
        # print("AuthorizationsInline.get_max_num", len(self.model.doc_type.field.choices), self.model.doc_type.field.choices, dir(self.model.doc_type.field.choices))
        if obj:
            if request.user.profile.institution and obj.status == 'c':
                return len(self.model.doc_type.field.choices)
            else:
                return 0
        return 0
        
    def get_readonly_fields(self, request, obj=None):
        # print("AuthorizationsInline.get_readonly_fields", obj)
        if request.user.is_superuser:
            return []
        if obj:
            # print("AuthorizationsInline obj.institution", obj.institution)
            # print("AuthorizationsInline request", request.user.institutions.institutions.all())
            # print(obj.institution in request.user.institutions.institutions.all())
            if request.user.profile.institution and obj.status == 'c':
                # print("AuthorizationsInline.get_readonly_fields modify")
                return []
            else:
                # print("AuthorizationsInline.get_readonly_fields not modify")
                return self.readonly_fields_not_modify
        return super().get_readonly_fields(request, obj)
    
    def get_formset(self, request, obj=None, **kwargs):
        # print("AuthorizationsInline.get_formset")
        # self.readonly_fields = ()
        # self._set_status_form(request, obj, **kwargs)
        if request.user.is_superuser:
            self.can_delete = True
            return super().get_formset(request, obj, **kwargs)
        if obj:
            if request.user.profile.institution and obj.status == 'c':
                # print("AuthorizationsInline.get_readonly_fields not modify")
                self.can_delete = True
            else:
                # print("AuthorizationsInline.get_readonly_fields modify")
                self.can_delete = False
        return super().get_formset(request, obj, **kwargs)
        

@admin.register(Protocol)
class ProtocolAdmin(admin.ModelAdmin, StatusManager):
    form = ProtocolForm
    change_form_template = "admin/change_form_protocol.html"
    inlines_add = ()
    inlines_add_session = (SessionInline, )
    inlines_add_learner = (SessionInline, LearnersInline)
    inlines_add_files = (SessionInline, LearnersInline, AuthorizationsInline, FilesInline)
    ordering = ['-pk']
    autocomplete_fields = ['course', 'owner', 'center', 'institution']
    list_display = ('__str__', 'type', 'title', 'code', 'status', "owner", "center")
    search_fields = ["id", "course__feature__title", "course__code", 
                        "session__trainer__last_name",
                        "session__trainer__first_name",
                        "learners__user__last_name",
                        "learners__user__first_name",
                    ]
    list_filter = (
        "type",
        "status",
        ("session__country", admin.RelatedOnlyFieldListFilter),
    )
    readonly_fields_add = ("owner", "status", "center", "institution")
    readonly_fields_default = ("owner", "status")
    readonly_fields_all     = ["owner", "status"]  + ["course","type","learners_request","status","center", "institution"]
    
    class Media:
        css = {
            'all': (
            'css/digisafe.css',
            "/static/admin/css/forms.css",
            "/static/css/site.css",
            )
            }
        js = (
            # 'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js',
            # 'https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js',
        )

    def get_exclude(self, request, obj=None):
        fields = []
        if obj:
            if obj.course.need_institution == True:
                fields = []
            else:
                fields = ["institution"]
            return fields      
        # Creazione nuovo protocollo click su +Add
        return ["institution"]        
        
    def get_readonly_fields(self, request, obj=None):
        # print("ProtocolAdmin.get_readonly_fields")
        fields = []
        if request.user.is_superuser:
            return fields
        fields = []
        if obj:
            need_institution = obj.course.need_institution
            if obj.course.need_institution == True:
                readonly_fields_default = ["owner", "status", "institution"]
                readonly_fields_all     = ["owner", "status"]  + ["course","type","learners_request","center", "institution"]
            else:
                readonly_fields_default = ["owner", "status"]
                readonly_fields_all     = ["owner", "status"]  + ["course","type","learners_request","center"]
            
            if obj.status == "m" and request.user.profile.trainer:
                fields = readonly_fields_default
            if obj.status == "m" and request.user.profile.director:
                fields = readonly_fields_all
            if obj.status == "m" and request.user.profile.institution:
                fields = readonly_fields_all
            
            if obj.status == "r"  and request.user.profile.trainer:
                fields = readonly_fields_all
            if obj.status == "r"  and request.user.profile.director:
                fields = readonly_fields_all
                if need_institution: fields.remove("institution")
            if obj.status == "r" and request.user.profile.institution:
                fields = readonly_fields_all
                
            if obj.status == "c"  and request.user.profile.trainer:
                fields = readonly_fields_all
            if obj.status == "c"  and request.user.profile.director:
                fields = readonly_fields_all
            if obj.status == "c" and request.user.profile.institution:
                fields = readonly_fields_all
                
            if obj.status == "a"  and request.user.profile.trainer:
                fields = readonly_fields_all
            if obj.status == "a"  and request.user.profile.director:
                fields = readonly_fields_all
            if obj.status == "a" and request.user.profile.institution:
                fields = readonly_fields_all
                
            if obj.status == "t"  and request.user.profile.trainer:
                fields = readonly_fields_all
            if obj.status == "t"  and request.user.profile.director:
                fields = readonly_fields_all
            if obj.status == "t" and request.user.profile.institution:
                fields = readonly_fields_all
                
            if obj.status == "h":
                fields = readonly_fields_all
            return fields
        else:
            # Creazione nuovo protocollo click su +Add
            readonly_fields_add = ["owner", "status", "center"]
            return readonly_fields_add
        
    def add_view(self, request, form_url='', extra_context=None):
        # print("ProtocolAdmin.add_view")
        return super().add_view(request, form_url, extra_context)
        
    def change_view(self, request, object_id, form_url='', extra_context=None):
        # print("ProtocolAdmin.change_view", object_id)
        if object_id:
            obj = Protocol.objects.get(pk=object_id)
            if not extra_context:
                    extra_context = {}          
            # extra_context["checknumtrainer"] =  obj.checkNumTrainer()
            extra_context["protocol"] =  obj
            extra_context["status_form"] =  self.status_form
            extra_context["app_name"] =  obj._meta.app_label
            extra_context["model_name"] =  self.model.__name__.lower()
        extra_context = self._set_status_change_view(request, object_id, form_url, extra_context)
        # print("ProtocolAdmin.change_view extra_context", extra_context)
        return super().change_view(
            request, object_id=object_id, form_url=form_url, extra_context=extra_context)
    
    def response_change(self, request, obj):
        # print("ProtocolAdmin.response_change")
        resp = self._set_status_response_change(request, obj)
        
        return super().response_change(request, obj)
        
    def response_add(self, request, obj, post_url_continue=None):
        # dopo che viene aggiunto un nuovo protocollo ritorna al chenge per inserire i forms in line
        if obj.pk:
            return HttpResponseRedirect("../%s/change/"%obj.pk)
        return super().response_add(request, obj, post_url_continue)
        
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        extra_urls = [
            path('<int:pk>/actions/', self.admin_site.admin_view(self.actions_view), name='actions-list'),
            path('<int:pk>/certificate/list/', self.admin_site.admin_view(self.certificate_list), name='certificate-list'),
            path('<int:pk>/user/<int:user_id>/view/', self.admin_site.admin_view(self.certificate_user), name='certificate-user'),
            path('<int:pk>/file/<int:file_id>/sign/', self.admin_site.admin_view(self.sign_file), name='sign-file'),
        ]
        return extra_urls + urls
    
    def sign_file(self, request, pk=None, file_id=None):
        if not pk==None:
            f = Files.objects.get(pk=file_id)
            protocol = f.protocol
            context = dict(
                    # Include common variables for rendering the admin template.
                   self.admin_site.each_context(request),
                   # Anything else you want in the context...
                   opts=self.opts,
                   module_name=self.model._meta.model.__name__,
                   media=self.media,
                   object=protocol,
                   
                   file = f, 
                   filename = f.get_doc_type_display,
                   protocol = protocol,
                )
            return TemplateResponse(request, 'protocol/sign_file.html', context)
        
    def actions_view(self, request, pk=None):
        # print("ProtocolAdmin.actions_view request",request)
        if not pk == None: 
            protocol = Protocol.objects.get(pk=pk)
            objects_list = Action.objects.filter(protocol=protocol).order_by("-pk")
            # print("ProtocolAdmin.actions_view each_context", self.admin_site.each_context(request))
            # print("ProtocolAdmin.actions_view media", self.media)
            context = dict(
               # Include common variables for rendering the admin template.
               self.admin_site.each_context(request),
               # Anything else you want in the context...
               objects_list = objects_list,
               opts=self.opts,
               object=protocol,
               module_name=self.model._meta.model.__name__,
               media=self.media,
            )
        return TemplateResponse(request, "protocol/action_list.html", context)
    
    def certificate_list(self, request, pk=None):
        # print("ProtocolAdmin.actions_view request",request)
        if not pk == None: 
            protocol = Protocol.objects.get(pk=pk)
            objects_list = protocol.learners_set.filter(passed=True).order_by("pk")
            # print("ProtocolAdmin.actions_view each_context", self.admin_site.each_context(request))
            # print("ProtocolAdmin.actions_view media", self.media)
            context = dict(
               # Include common variables for rendering the admin template.
               self.admin_site.each_context(request),
               # Anything else you want in the context...
               objects_list = objects_list,
               opts=self.opts,
               object=protocol,
               module_name=self.model._meta.model.__name__,
               media=self.media,
            )
        return TemplateResponse(request, "protocol/certificate_protocol_list.html", context)
    
    def certificate_user(self, request, pk=None, user_id=None):
        from utils.helper import qrcode_str2base64
        from django.contrib.sites.shortcuts import get_current_site
        # print("ProtocolAdmin.actions_view request",request)
        if not pk == None:            
            protocol = Protocol.objects.get(pk=pk)
            trainer = User.objects.get(pk=user_id)
            full_url = ''.join(['http://', get_current_site(request).domain, "protocol/", str(protocol.id), "/user/", str(trainer.id),"/check/"])
            
            #todo: implementazione del codice qr del certificato
            if settings.DEBUG:
                full_url = ''.join(['http://', "192.168.10.104:8000/", "protocol/", str(protocol.id), "/user/", str(trainer.id),"/check/"])
            # print("ProtocolAdmin.certificate_user full_url", full_url)
            
            context = dict(
               # Include common variables for rendering the admin template.
               self.admin_site.each_context(request),
               # Anything else you want in the context...
               trainer = trainer,
               opts=self.opts,
               protocol=protocol,
               module_name=self.model._meta.model.__name__,
               media=self.media,
               web_site="digisafe.ircot.co.uk",
               qrcode_img= qrcode_str2base64(full_url)
            )
        return TemplateResponse(request, "protocol/certificate_user.html", context)
        
    def get_form(self, request, obj=None, **kwargs):
        # print("ProtocolAdmin.get_form kwargs", kwargs)
        kwargs = self._set_status_form(request, obj=None, **kwargs)
        # print("ProtocolAdmin.get_form kwargs", kwargs)
        return super().get_form(request, obj, **kwargs)
        
    def get_inline_instances(self, request, obj=None):
        # solamente dopo che viene aggiunto protocollo visualizza i forms in line
        # print("get_inline_instances", obj.session_set.count())
        # inlines_add = ()
        # inlines_add_session = (SessionInline, )
        # inlines_add_learner = (SessionInline, LearnersInline)
        status_full = ["m", "r", "c", "a", "t", "h"]
        inlines_full = [SessionInline, LearnersInline, AuthorizationsInline, FilesInline]
        inlines = []
        if obj:
            # Trainer user
            if request.user.profile.trainer:
                if obj.status in status_full and obj.session_set.count() > 0:
                    return [inline(self.model, self.admin_site) for inline in inlines_full]
                else:
                    return [inline(self.model, self.admin_site) for inline in [SessionInline,]]
            
            # Director user
            if request.user.profile.director:
                if obj.status in ["r", "c"]:
                    return [inline(self.model, self.admin_site) for inline in [SessionInline]]
                if obj.status in ["a"]:
                    return [inline(self.model, self.admin_site) for inline in [SessionInline, AuthorizationsInline]]
                if obj.status in ["t", "h"]:
                    return [inline(self.model, self.admin_site) for inline in [SessionInline, LearnersInline, FilesInline]]
            
            # Institution user
            if request.user.profile.institution:
                if obj.status in ["c", "a"]:
                    return [inline(self.model, self.admin_site) for inline in [SessionInline, AuthorizationsInline]]
                if obj.status in ["t", "h"]:
                    return [inline(self.model, self.admin_site) for inline in inlines_full]
                    
        return inlines
    
    def get_queryset(self, request):
        # print("ProtocolAdmin.get_queryset")
        u_superuser = request.user.is_superuser
        tab = userprofile2bit(request.user)
        query = super().get_queryset(request)
        query_list = []
        if not u_superuser: 
            if protocol_perm(request.user, TRA): 
                #visualizza i protocolli creati dall'utente loggato
                query_list.append(query.filter(Q(owner=request.user)))
                pass
            if protocol_perm(request.user, DIR):
                #visualizza i protocolli creati + centri da direttore
                try:
                    own_centers = request.user.trainingcenter.centers.all()
                    query_list.append(query.filter(Q(center__in=own_centers)))
                except ObjectDoesNotExist:
                    pass
            if protocol_perm(request.user, INS):
                own_institutions = request.user.institutions.institutions.all()
                query_list.append(query.filter(Q(institution__in=own_institutions)))
            res = query_list[0]        
            for q in query_list[1:]:
                res = res | q 
            return res
        return query
        
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        # print("ProtocolAdmin.get_search_results", request.path)
        if request.path == '/admin/autocomplete/' and request.GET.get("field_name") == "trainer":
            queryset = queryset.filter(trainer__profile__trainer=1)
        return queryset, use_distinct
    
    def save_model(self, request, obj, form, change):
        # print("ProtocolAdmin.save_model", obj)
        if getattr(obj, 'owner', None) is None:
            # Lo esegue solo alla creazione del nuovo record
            obj.owner = request.user
            obj.save()
            self.setAction(obj, request.user, _("Create new protocol"))
        return super().save_model(request, obj, form, change)
        
    def delete_model(self, request, obj):
        if request.user.is_superuser:
            return super().delete_model(request, obj)
        if obj.status != "h":
            return super().delete_model(request, obj)
            
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            # print("ProtocolAdmin.save_formset instance", instance.__class__.__name__, instance.pk, change)
            if instance.__class__.__name__ == "Files" and instance.pk == None:
                # solo alla creazione del nuovo oggetto inserisce l'utente owner
                instance.owner = request.user
            if instance.__class__.__name__ == "Authorizations" and instance.pk == None:
                # solo alla creazione del nuovo oggetto inserisce l'utente owner
                instance.owner = request.user
            instance.save()
            
        formset.save_m2m()
        
    def setAction(self, protocol, owner, text, info=""):
        if protocol:
            a = Action(protocol=protocol, owner=owner, text=text, info=info)
            a.save()

    # status 'default'        
    def _set_status_response_change_default(self, request, obj):
        return
        # if not obj: return
        # text = ""
        # if request.POST.get("_richiestaprotocol", False):
            # obj.status = "r"
            # text = _("Set request")
        # elif request.POST.get("_autorizzaprotocol", False):
            # obj.status = "a"
            # text = _("Set authorized")
        # elif request.POST.get("_negaprotocol", False):
            # obj.status = "n"
            # text = _("Set denied")
        # elif request.POST.get("_terminarotocol", False):
            # obj.status = "t"
            # text = _("Set finish")
        # elif request.POST.get("_chiudiprotocol", False):
            # obj.status = "h"
            # text = _("Set close")
        # obj.save()
        # if text:
            # self.setAction(obj, request.user, text)
        return
        
    def _set_status_form_default(self, request, obj, **kwargs):
        # print("ProtocolAdmin._set_status_form_default", self.readonly_fields)
        # self.readonly_fields = self.readonly_fields_default
        # if obj:
            # if obj.course.need_institution == False:
                # self.exclude = ["institution",]
        return kwargs
    
    # status 'm'
    def _set_m_status_form(self, request, obj, **kwargs):
        # print("set_m_status_form", self.readonly_fields)
        # self.readonly_fields = self.readonly_fields + ("course",)
        if obj.owner == request.user:
           kwargs = self._set_status_form_default(request, obj, **kwargs)
           # self.readonly_fields = self.readonly_fields + ("institution",)
           return kwargs
        # self.readonly_fields = self.readonly_fields_all
        return
    
    def _set_m_status_change_view(self, request, object_id, form_url, extra_context):
        # return super()._set_m_status_change_view(request, object_id, form_url, extra_context)
        if object_id:
            check = Protocol.objects.get(pk=object_id).checkAll()
            if check:
                return super()._set_m_status_change_view(request, object_id, form_url, extra_context)
        return extra_context
    
    def _set_m_status_response_change(self, request, obj):
        """Status 'm'. Il trainer decide di richiedere autorizzazione a direttore e/o ente
        """
        text = ""
        if request.POST.get("_richiestaprotocol", False):
            # print("ProtocolAdmin._set_m_status_response_change _richiestaprotocol")
            # Procede con lo status successivo 'c'
            obj.status = "r"
            text = _("Set request")
            pass
        if text:
            obj.save()
            self.setAction(obj, request.user, text)
            
    # status 'r'
    def _set_r_status_form(self, request, obj, **kwargs):
        # print("ProtocolAdmin.set_r_status_form status", obj.status)
        kwargs = self._set_status_form_default(request, obj, **kwargs)
        u_superuser = request.user.is_superuser
        return kwargs
    
    def _set_r_status_change_view(self, request, object_id, form_url, extra_context):
        # print("ProtocolAdmin._set_r_status_change_view")
        if object_id:
            obj = Protocol.objects.get(pk=object_id)
            if request.user.profile.director and obj.course.need_institution == False:
                    extra_context.update(status_form=DeniedConfirmForm())
        return extra_context
        
    def _set_r_status_response_change(self, request, obj):
        """Status 'r'. Il direttore decide di caricare oppure declinare.
        Quando declina rimanda ad un form per indicarne la motivazione
        """
        # print("ProtocolAdmin._set_r_status_response_change")
        
        from django.contrib.admin import helpers
        
        text = info = ""
        form = DeniedConfirmForm(request.POST)
        if request.POST.get("_caricaprotocol", False) and obj.course.need_institution == True:
            # print("ProtocolAdmin._set_r_status_response_change _caricaprotocol")
            # Procede con lo status successivo 'c'
            if obj.course.need_institution:
                if not obj.institution:
                    messages.add_message(request, messages.ERROR, _('{0} Need an institution. Choice one. Status wasn\'t change.'.format(obj)))
                    return
            obj.status = "c"
            text = _("Set load by director")
            pass
        elif request.POST.get("_autorizzaprotocol", False) and obj.course.need_institution == False:
            # print("ProtocolAdmin._set_r_status_response_change _caricaprotocol")
            # Procede con lo status successivo 'c'
            obj.status = "a"
            text = _("Set authorized by director")
            pass
        elif request.POST.get("_declinaprotocol", False):
            # print("ProtocolAdmin._set_r_status_response_change _declinaprotocol")
            # print("ProtocolAdmin._set_r_status_response_change form.is_valid()", form.is_valid())
            if form.is_valid():
                # Cambia lo stato solo con le informazioni aggiutne
                info = form.cleaned_data['info_denied']
                text = _("Set denied by director")
                obj.status = "m"
        if text:
            obj.save()
            self.setAction(obj, request.user, text, info)

    #    status 'c'
    def _set_c_status_form(self, request, obj, **kwargs):
        # print("ProtocolAdmin.set_c_status_form status", obj.status)
        kwargs = self._set_status_form_default(request, obj, **kwargs)
        u_superuser = request.user.is_superuser
        return kwargs
        
    def _set_c_status_change_view(self, request, object_id, form_url, extra_context):
        # print("ProtocolAdmin._set_c_status_change_view")
        if object_id:
            obj = Protocol.objects.get(pk=object_id)
            if request.user.profile.institution and obj.course.need_institution == True:
                extra_context.update(status_form=DeniedConfirmForm())
        return extra_context
    
    def _set_c_status_response_change(self, request, obj):
        """Status 'c'. l'ente decide di autorizzare oppure declinare.
        Quando declina chiede di indicarne la motivazione
        """
        # print("ProtocolAdmin._set_c_status_response_change")
        
        from django.contrib.admin import helpers
        
        text = info = ""
        form = DeniedConfirmForm(request.POST)
        
        if request.POST.get("_autorizzaprotocol", False):
            # print("ProtocolAdmin._set_c_status_response_change _autorizzaprotocol")
            # Procede con lo status successivo 'c'
            obj.status = "a"
            # obj.institution = request.user
            text = _("Set authorized from institution")
            pass
        elif request.POST.get("_negaprotocol", False):
            # print("ProtocolAdmin._set_c_status_response_change _negaprotocol")
            # print("ProtocolAdmin._set_c_status_response_change form.is_valid()", form.is_valid())
            if form.is_valid():
                # Cambia lo stato solo con le informazioni aggiutne
                info = form.cleaned_data['info_denied']
                text = _("Set denied from institution. Return modify.")
                obj.status = "m"
        if text:
            obj.save()
            self.setAction(obj, request.user, text, info)

    #    status 'a'
    def _set_a_status_form(self, request, obj, **kwargs):
        # print("ProtocolAdmin.set_a_status_form status", obj.status)
        kwargs = self._set_status_form_default(request, obj, **kwargs)
        u_superuser = request.user.is_superuser
        return kwargs
        
    def _set_a_status_change_view(self, request, object_id, form_url, extra_context):
        # print("ProtocolAdmin._set_a_status_change_view")
        # extra_context.update(status_form=DeniedConfirmForm())
        p = Protocol.objects.get(pk=object_id)
        if request.user.profile.trainer and p.owner == request.user:
            if p.course.need_institution and p.institution.use_custom_files:
                extra_context['custom_institution_files'] = True
                extra_context['object_custom_institution_files'] = p.institution.institutioncustomfiles_set.all()
                f = p.institution.institutioncustomfiles_set.all()[0]
                print(dir(f))
            else:
                extra_context['attendance_register_view'] = True
                extra_context['exam_reporte_view'] = True
            if p.warning:
                extra_context['integration_info_form'] = IntegrationInfoForm()
        return extra_context
    
    def _set_a_status_response_change(self, request, obj):
        """Status 'a'. Il protocollo passa al trainer richiedente per inserimento docenti e documenti.
        """
        # print("ProtocolAdmin._set_a_status_response_change")
                
        text = info = ""
        form = IntegrationInfoForm(request.POST)
        if request.POST.get("_terminaprotocol", False):
            # print("ProtocolAdmin._set_a_status_response_change _terminaprotocol")
            # Procede con lo status successivo di chiusura 't'
            obj.status = "t"
            obj.warning = False
            text = _("Set finish")
            info = form['info'].value()
            pass
        if text:
            obj.save()
            self.setAction(obj, request.user, text, info)

    #    status 't'
    def _set_t_status_form(self, request, obj, **kwargs):
        # print("ProtocolAdmin.set_t_status_form status", obj.status)
        kwargs = self._set_status_form_default(request, obj, **kwargs)
        u_superuser = request.user.is_superuser
        # print("ProtocolAdmin.set_t_status_form self.readonly_fields", self.readonly_fields)
        return kwargs
        
    def _set_t_status_change_view(self, request, object_id, form_url, extra_context):
        # print("ProtocolAdmin._set_t_status_change_view")
        if object_id:
            obj = Protocol.objects.get(pk=object_id)
            
            # Direttore
            if request.user.profile.director: #and obj.course.need_institution == False:
                extra_context.update(status_form=DeniedConfirmForm())
                f_exam = obj.files_set.filter(doc_type="v")
                f_register = obj.files_set.filter(doc_type="r")
                if f_exam:
                    extra_context.update(sign_file_exam=f_exam[0])
                if f_register:
                    extra_context.update(sign_file_register=f_register[0])  
            
            # Ente
            if request.user.profile.institution and obj.course.need_institution == True and obj.checkAllSignedFiles():
                extra_context.update(status_form=DeniedConfirmForm())
        
        return extra_context 
        
    def _set_t_status_response_change(self, request, obj):
        """Status 't'. Il protocollo passa al controllo del direttore e del'ente.
        """
        # print("ProtocolAdmin._set_t_status_response_change")
        
        from django.contrib.admin import helpers
        
        text = info = ""
        form = DeniedConfirmForm(request.POST)
        
        if request.POST.get("_chiudiprotocol", False): #in caso di solo direttore
            # print("ProtocolAdmin._set_a_status_response_change _chiudiprotocol")
            # Procede con lo status successivo di chiusura 'h'
            obj.status = "h"
            text = _("Set close")
            pass
        if request.POST.get("_negaprotocol", False): #in caso di richiesta integrazione
            # print("ProtocolAdmin._set_a_status_response_change _negaprotocol")
            # Procede con lo status successivo di chiusura 'h'
            if request.user.profile.director: obj.status = "a"
            if request.user.profile.institution: obj.status = "t"
            
            text = _("Request integration.")
            info = form['info_denied'].value()
            obj.warning = True
        if text:
            obj.save()
            self.setAction(obj, request.user, text, info)
        
        if obj.course.need_institution and obj.checkAllSignedFiles() and not obj.checkAllCertificateLoads():
                for u in obj.learners_set.filter(passed=True, inst_cert=""):
                    messages.add_message(request, messages.WARNING, _('{0}\'s Certificate has not been loaded yet.'.format(u.user.getFullName())))
            
    #    status 'h'
    def _set_h_status_form(self, request, obj, **kwargs):
        # print("ProtocolAdmin.set_h_status_form status", obj.status)
        kwargs = self._set_status_form_default(request, obj, **kwargs)
        u_superuser = request.user.is_superuser
        # print("ProtocolAdmin.set_t_status_form self.readonly_fields", self.readonly_fields)
        return kwargs
        
    def _set_h_status_change_view(self, request, object_id, form_url, extra_context):
        # print("ProtocolAdmin._set_h_status_change_view")
        if object_id:
            if request.user.profile.trainer or request.user.profile.director:
                learners = Protocol.objects.get(pk=object_id).learners_set.filter(passed=True)
                if learners:
                    context = dict(
                        certificate_view=True,
                        )
                    extra_context.update(context)
        return extra_context 
        
    def _set_h_status_response_change(self, request, obj):
        """Status 'h'. Il protocollo passa al trainer richiedente per inserimento docenti e documenti.
        """
        # print("ProtocolAdmin._set_h_status_response_change")
        pass

    
