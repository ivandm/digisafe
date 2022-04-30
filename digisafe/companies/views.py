from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.models import Q
from django.views.generic import ListView
from django.views import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib import messages
from django.utils.safestring import mark_safe

import datetime

from users.models import User
from agenda.models import Agenda
from .models import Company, requestAssociatePending, SessionBook, DateBook
from .forms import SessionBookForm, SessionBookUpdateForm, SettingsForm, ProfileFormSet


# todo: Sviluppare form di Ricerca Book sessions
# todo: Sviluppare Template Company Settings


@login_required(login_url="/account/login/")
def home(request):
    print("companies.views.home")
    companies = Company.objects.filter(admins=request.user)
    print(request.user.associates_company.filter(active=True))
    print(companies)
    return render(request, template_name='companies/select.html', context={'company_list': companies})


@login_required(login_url="/account/login/")
def set_company(request, pk=None):
    if pk:
        u = request.user
        c = Company.objects.filter(pk=pk, admins=u)
        # print(c.associates.all())
        if c:
            c = c[0]
            request.session["company_id"] = pk
            request.session["company_name"] = c.name
    return redirect("companies:home")


@method_decorator(login_required, name='dispatch')
class SettingsCompanyView(UpdateView):
    template_name = "companies/settings.html"
    form_class = SettingsForm
    model = Company

    def setup(self, request, *args, **kwargs):
        """
        Necessario override di Setup per assegnare 'pk'
        """
        # print("companies.views.SettingsCompanyView.setup")
        pk = request.session.get("company_id")
        kwargs.update(pk=pk)
        return super(SettingsCompanyView, self).setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super(SettingsCompanyView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['form'] = SettingsForm(self.request.POST, instance=self.object)
            data['profile'] = ProfileFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['form'] = SettingsForm(instance=self.object)
            data['profile'] = ProfileFormSet(instance=self.object)
        return data

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        profilo_form = ProfileFormSet(self.request.POST,  self.request.FILES, instance=self.object)
        if form.is_valid() and profilo_form.is_valid():
            return self.form_valid(form, profilo_form)
        else:
            return self.form_invalid(form, profilo_form)

    def form_valid(self, form, profilo_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        self.object = form.save()
        profilo_form.instance = self.object
        profilo_form.save()
        messages.add_message(self.request, messages.SUCCESS,
                             _(mark_safe("Settings <b>{}</b> have been just modified.".format(self.object))))
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, profilo_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form,
                                  profile=profilo_form,
                                  ))

    def get_success_url(self):
        return reverse_lazy("companies:setting")


@login_required(login_url="/account/login/")
def companyDetailView(request, pk=None):
    # print("companyDetailView")
    context = {}
    if pk:
        u = request.user
        c = Company.objects.filter(pk=pk, admins=u)
        # print(c.associates.all())
        if c:
            c = c[0]
            qs_results = Agenda.objects.filter(user__associates_company=c)
            request.session["company_id"] = pk
            context.update(company=c)
            context.update(sessionbook_list=SessionBook.objects.filter(company=c))
            context.update(qs_results=qs_results)
            # url per la ricerca dei markers jobprofile home position sulla mappa
            context.update(api_markers_agenda_url="/maps/api/agendafree/")
            # url per la ricerca dei markers jobprofile home position sulla mappa
            context.update(api_markers_agendabusy_url="/maps/api/agendabusy/")
            # url per la ricerca dei markers agenda sulla mappa
            context.update(api_markers_defaultposition_url="/maps/api/defaultposition/")
            context.update(api_search_job_url="/maps/api/search_job/")  # url per la ricerca dei markers sulla mappa
            return render(request, "companies/index.html", context)
    return redirect("account:index")


@login_required(login_url="/account/login/")
def retrieve_users_to_associate(request):
    # print("retrieve_users_to_associate.retrieve", request)
    slug = request.POST.get('slug')
    company_id = request.session.get("company_id")
    if company_id and slug:
        c = Company.objects.get(pk=company_id)
        user_list = User.objects.filter(
                                         Q(last_name__icontains=slug) | Q(first_name__icontains=slug)
                                        ).exclude(id__in=c.associates.all())
        return render(request, template_name='companies/get_user_list_detail.html', context={'object_list': user_list})
    raise Http404(_("No users matches the given query."))


@method_decorator(login_required, name='dispatch')
def companyPublicDetailView(request, pk=None):
    context = {}
    if pk:
        c = Company.objects.get(pk=pk)
        request.session["company_id"] = pk
        context.update(company=c)
    return render(request, "companies/public_view.html", context)


@login_required(login_url="/account/login/")
def requestAssociateAction(request):
    request_id = request.POST.get("request_id")
    action = request.POST.get("action")  # accept/refuse
    if request_id:
        r = requestAssociatePending.objects.get(pk=request_id)
        c = r.company
        u = r.user
        if u == request.user:
            if action == "accept":
                c.associates.add(u)
                r.delete()
                return JsonResponse({'accept': 'ok'})
            elif action == "refuse":
                r.delete()
                return JsonResponse({'refuse': 'ok'})

    return JsonResponse({'nothing': 'ok'})


@login_required(login_url="/account/login/")
def requestDissociateAction(request, pk):
    company_id = pk
    user_id = request.POST.get("user_id")
    if company_id:
        c = Company.objects.get(pk=company_id)
        u = c.associates.filter(pk=user_id)
        if u:
            c.associates.remove(u[0])
            return JsonResponse({'dissociate': True})
    return JsonResponse({'dissociate': False})


@login_required(login_url="/account/login/")
def requestAssociateToUser(request):
    # Company chiede associazione ad un utente
    user_id = request.GET.get("user_id")
    company_id = request.session.get("company_id")
    if user_id and company_id:
        u = User.objects.get(pk=user_id)
        admin_u = request.user
        c = Company.objects.filter(pk=company_id, admins=admin_u)
        if c:
            c = c[0]
            r = requestAssociatePending(user=u, company=c, company_req=True)
            r.save()
            return JsonResponse({'save': 'ok'})
    return JsonResponse({})


@login_required(login_url="/account/login/")
def requestAssociateToCompany(request):
    # Utente chiede associazione ad una Company
    user_id = request.GET.get("user_id")
    company_id = request.GET.get("company_id")
    if user_id and company_id:
        u = User.objects.get(pk=user_id)
        c = Company.objects.get(pk=user_id)
        if u == request.user:  # utente chiede associazione a company
            r = requestAssociatePending(user=u, company=c, user_req=True)
        else:
            r = requestAssociatePending(user=u, company=c, company_req=True)
        r.save()
        return JsonResponse({'save': 'ok'})
    return JsonResponse({})

# MAP


@login_required(login_url="/account/login/")
def openMap(request, session_id=None):
    # print("companyDetailView")
    context = {}
    if session_id:
        u = request.user
        company_id = request.session.get("company_id")
        c = Company.objects.filter(pk=company_id, admins=u)
        # print(c.associates.all())
        if c:
            c = c[0]
            qs_results = Agenda.objects.filter(user__associates_company=c)
            sb = SessionBook.objects.get(company=c, id=session_id)
            context.update(company=c)
            context.update(sessionbook=sb)
            context.update(initial_date_start="{}-{:02d}-{:02d}".format(sb.start_date.year,
                                                                        sb.start_date.month, sb.start_date.day))
            context.update(initial_date_end="{}-{:02d}-{:02d}".format(sb.end_date.year,
                                                                      sb.end_date.month, sb.end_date.day))
            context.update(qs_results=qs_results)
            context.update(favoriteuser_url=reverse('companies:favoriteuser'))  # add/remove favorite user
            context.update(optionlist_url=reverse('companies:optionusers',
                                                  args=[session_id]))  # add/remove option list user
            context.update(retrive_optionlist_url=reverse('companies:retriveoptionlist',
                                                          args=[session_id]))  # add/remove option list user
            context.update(user_job_info_url=reverse('job:user-job-info'))
            # url per la ricerca dei markers jobprofile home position sulla mappa
            context.update(api_markers_agenda_url="/maps/api/agendafree/")
            # url per la ricerca dei markers jobprofile home position sulla mappa
            context.update(api_markers_agendabusy_url="/maps/api/agendabusy/")
            # url per la ricerca dei markers agenda sulla mappa
            context.update(api_markers_defaultposition_url="/maps/api/defaultposition/")
            context.update(api_search_job_url="/maps/api/search_job/")  # url per la ricerca dei markers sulla mappa
            return render(request, "companies/openmap.html", context)
    return redirect("account:index")


# BOOKING


@method_decorator(login_required, name='dispatch')
class SessionBookListView(ListView):
    model = SessionBook
    context_object_name = "sessionbook_list"
    ordering = ["-expire_date"]
    paginate_by = 20

    def get_queryset(self):
        querystring = self.request.GET.get("qs")
        company_id = self.request.session.get("company_id")
        qs = SessionBook.objects.filter(company__id=company_id)
        if querystring:
            qs = qs.filter(Q(name__icontains=qs) | Q(note__icontains=qs))
        return qs


@method_decorator(login_required, name='dispatch')
class SessionBookCreateView(CreateView):
    model = SessionBook
    form_class = SessionBookForm

    def form_valid(self, form):
        company_id = self.request.session.get("company_id")
        c = Company.objects.get(pk=company_id)
        form.instance.company = c
        sb = form.save()

        # crea DateBook per ogni giorno del range date_start/date_end
        sd = form.cleaned_data['start_date']
        ed = form.cleaned_data['end_date']
        delta = ed - sd
        for i in range(delta.days + 1):
            day = sd + datetime.timedelta(days=i)
            db = DateBook(session=sb, date=day)
            db.save()

        return super().form_valid(form)

    def get_success_url(self):
        company_id = self.request.session.get("company_id")
        return reverse_lazy("companies:sessionbook-list")


@method_decorator(login_required, name='dispatch')
class SessionBookUpdateView(UpdateView):
    model = SessionBook
    form_class = SessionBookUpdateForm

    def form_valid(self, form):
        # print("companies.SessionBookUpdateView.form_valid")
        sb = self.object
        # print(sb.datebook_set.all())
        # print(sb.start_date)
        # print(form.cleaned_data['start_date'])
        # se hanno cambiato start_date e end_date ...
        if form.has_changed():
            if 'start_date' in form.changed_data or 'end_date' in form.changed_data:
                # 1) cancella tutti i dati DateBook collegati alla sessione di SessionBook
                sb.datebook_set.all().delete()
                # 2) crea nuovi valori DateBook per ogni giorno del nuovo range date_start/date_end
                sd = form.cleaned_data['start_date']
                ed = form.cleaned_data['end_date']
                delta = ed - sd
                for i in range(delta.days + 1):
                    day = sd + datetime.timedelta(days=i)
                    db = DateBook(session=sb, date=day)
                    db.save()

        return super().form_valid(form)

    def get_success_url(self):
        company_id = self.request.session.get("company_id")
        return reverse_lazy("companies:sessionbook-list")


@method_decorator(login_required, name='dispatch')
class SessionBookDeleteView(DeleteView):
    model = SessionBook
    success_url = reverse_lazy('companies:sessionbook-list')


@method_decorator(login_required, name='dispatch')
class SessionBookDetailView(View):
    """
    Visualizza il template con i dettagli della Work Session e le date.
    L'utente decide quali date confermare.
    """
    model = SessionBook
    template_name = 'account/sessionbook_detail.html'
    pk = None

    def get_session_object(self, *args, **kwargs):
        # print("companies.views.SessionBookDetailView.get_session_object")
        request = kwargs['request']
        if request.method == "GET":
            uuid = request.GET.get("uuid")
        if request.method == "POST":
            uuid = request.POST.get("uuid")
        now = timezone.now()
        # todo: se non trova una query, solleva un errore. Bisogna gestire correttamente con messaggi idonei
        if self.pk:
            return self.model.objects.get(pk=self.pk, uuid=uuid, expire_date__gte=now, user_option_list=request.user)
        return self.model.objects.none()

    def get(self, request, pk):
        self.pk = pk
        uuid = self.request.GET.get("uuid")
        now = timezone.now()
        obj = self.get_session_object(request=request)
        return render(request, self.template_name, {'object': obj})

    def post(self, request, pk):
        # print("companies.views.SessionBookDetailView.post")
        self.pk = pk
        obj = self.get_session_object(request=request)
        if obj:
            # print(request.POST)
            date_ids = self.request.POST.getlist("date_id", [])
            for date in obj.datebook_set.filter(id__in=date_ids).exclude(users=request.user):
                date.users.add(request.user)
                date.save()
                messages.add_message(request, messages.SUCCESS,
                                     mark_safe(_('You have booked the date <b>{}</b>'.format(date.date))))
            for date in obj.datebook_set.filter(users=request.user).exclude(id__in=date_ids):
                date.users.remove(request.user)
                date.save()
                messages.add_message(request, messages.WARNING,
                                     mark_safe(_('You have removed the booked date <b>{}</b>'.format(date.date))))
        return render(request, self.template_name, {'object': obj})


@login_required(login_url="/account/login/")
def favoriteuser(request):
    """
    Azione sil DB della Company.
    Aggiunge/Toglie un utente dai favoriti
    """
    # print("companies.views.favoriteuser")
    company_id = request.session.get("company_id", 1)
    c = Company.objects.get(id=company_id)
    user_id = request.GET.get("user_id")
    u = User.objects.get(id=user_id)
    if c.favorite.filter(pk=user_id):
        c.favorite.remove(u)
        favorite = False
    else:
        c.favorite.add(u)
        favorite = True
    return JsonResponse({'favorite': favorite})


@login_required(login_url="/account/login/")
def list_users_from_map(request, session_id):
    """
    Aggiunte/Toglie dalla lista 'list_users_from_map' in sessione
    un utente visualizzato sulla mappa
    """
    company_id = request.session.get("company_id", 1)
    c = SessionBook.objects.get(id=session_id, company__id=company_id)
    user_id = request.GET.get("user_id")
    u = User.objects.get(id=user_id)
    if c.user_option_list.filter(pk=user_id):
        c.user_option_list.remove(u)
        option = False
    else:
        c.user_option_list.add(u)
        option = True
    return JsonResponse({'option': option})


@login_required(login_url="/account/login/")
def retrive_users_from_map(request, session_id):
    """Render Template della lista di utenti selezionati dalla mappa"""
    company_id = request.session.get("company_id")
    sb = SessionBook.objects.get(id=session_id, company__id=company_id)
    listusers_obj = sb.user_option_list.all()
    if request.GET.get("json"):
        l_users = [
            {
                'user': x.getFullName,
                'id': x.id,
                'jobs': [y.title for y in x.jobprofile.job.all()]
            } for x in listusers_obj]
        return JsonResponse(l_users, safe=False)
    context = {
        "objects_list": listusers_obj
    }
    return render(request, "companies/list_users_from_map.html", context)


@login_required(login_url="/account/login/")
def book_user(request):
    """Richiesta di book da parte dell'impresa"""
    booked = False
    return JsonResponse({'booked': booked})


@login_required(login_url="/account/login/")
def send_invite_now(request, session_id):
    """
    Invia un messaggio d'invito agli utenti nella lista di SessionBook
    :param request: <request>
    :param session_id: int
    :return: json
    """
    s = SessionBook.objects.get(pk=session_id)
    s.send_book_invite()
    return JsonResponse({'send': True})


@login_required(login_url="/account/login/")
def response_user_invite(request, session_id):
    # todo: da implementare, forse!
    print("companies.views.response_user_invite")
    res = request.GET.get("book_response")
    uuid = request.GET.get("uuid")
    print(res)
    print(uuid)
    return JsonResponse({'send': True})


# end BOOKING
