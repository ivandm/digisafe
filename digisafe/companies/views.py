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
from .forms import SessionBookForm, SessionBookUpdateForm, DateBookFormSet, SettingsForm, \
    ProfileFormSet, SessionBookDetailForm
from pricelist.forms import SessionPriceForm
from pricelist.models import SessionPrice


# Home del menu Company, Seleziona la Company
@login_required(login_url="/account/login/")
def home(request):
    # print("companies.views.home")
    companies = Company.objects.filter(admins=request.user)
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
            messages.add_message(request, messages.SUCCESS,
                                 _(mark_safe("Company <b>{}</b> have been just selected.".format(c))))
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


# * BOOKING * #


@method_decorator(login_required, name='dispatch')
class SessionBookListView(ListView):
    model = SessionBook
    context_object_name = "sessionbook_list"
    # ordering = ["id"]
    paginate_by = 20

    def get_queryset(self):
        # print("companies.views.SessionBookListView.get_queryset")
        querystring = self.request.GET.get("qs")
        company_id = self.request.session.get("company_id")
        qs = SessionBook.objects.filter(company__id=company_id)
        if querystring:
            qs = qs.filter(Q(name__icontains=querystring) | Q(note__icontains=querystring)).order_by("expire_date")
        return qs.order_by("expire_date")


@method_decorator(login_required, name='dispatch')
class SessionBookCreateView(CreateView):
    model = SessionBook
    form_class = SessionBookForm

    def form_valid(self, form):
        # print("companies.views.SessionBookCreateView.form_valid")
        company_id = self.request.session.get("company_id")
        c = Company.objects.get(pk=company_id)
        form.instance.company = c
        sb = form.save()

        # crea DateBook per ogni Job scelto
        jobs = form.cleaned_data['jobs']
        sd = form.cleaned_data['start_date']
        ed = form.cleaned_data['end_date']
        for job in jobs:
            # crea DateBook per ogni giorno del range date_start/date_end
            delta = ed - sd
            for i in range(delta.days + 1):
                day = sd + datetime.timedelta(days=i)
                db = DateBook(session=sb, job=job, date=day)
                db.save()

        if self.request.POST.get("save_modify", False):
            return HttpResponseRedirect(reverse_lazy("companies:sessionbook-update", args=[sb.id]))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("companies:sessionbook-list")


@method_decorator(login_required, name='dispatch')
class SessionBookUpdateView(UpdateView):
    model = SessionBook
    form_class = SessionBookUpdateForm

    def get_context_data(self, **kwargs):
        data = super(SessionBookUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['form'] = SessionBookUpdateForm(self.request.POST, instance=self.object)
            data['dates_form'] = DateBookFormSet(
                self.request.POST, instance=self.object,
                queryset=self.object.datebook_set.order_by("job", "date"),)
        else:
            data['form'] = SessionBookUpdateForm(instance=self.object)
            data['dates_form'] = DateBookFormSet(
                instance=self.object,
                queryset=self.object.datebook_set.order_by("job", "date"),)
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

        dates_form = DateBookFormSet(self.request.POST, instance=self.object,
                                     queryset=self.object.datebook_set.order_by("job", "date"),
                                     )

        if form.is_valid() and dates_form.is_valid():
            return self.form_valid(form, dates_form)
        else:
            return self.form_invalid(form, dates_form)

    def form_valid(self, form, dates_form):
        # print("companies.SessionBookUpdateView.form_valid")
        sb = self.object

        # todo: bug. inserisce doppie date alcune volte
        # se hanno cambiato start_date or end_date or jobs ...
        if form.has_changed():
            # Preleva le scelte del FORM (no del formset)
            jobs_choosen = form.cleaned_data['jobs']  # Ritorna tipo QuerySet Job
            sd = form.cleaned_data['start_date']
            ed = form.cleaned_data['end_date']

            # Lista di tipi date dai valori inseriti nel FORM
            new_range_dates_list = [sd + datetime.timedelta(days=i) for i in range((ed-sd).days + 1)]
            # print("new_range_dates_list", new_range_dates_list)

            # Lista di nuovi tipi date che si aggiungono alle vecchie (se presenti)
            old_dates_list = [x.date for x in sb.datebook_set.all()]  # range date
            new_add_dates_list = [x for x in new_range_dates_list if x not in old_dates_list]
            # print("new_add_dates_list pre", new_add_dates_list)

            # Nuovi jobs che sono aggiunti nel FORM
            new_jobs_list = jobs_choosen.exclude(job_datebook__in=sb.datebook_set.all())
            # print("new_jobs_list pre", new_jobs_list)

            # Vecchi jobs che sono rimasti (non cancellati dal FORM)
            old_jobs_list = sb.jobs.filter(pk__in=jobs_choosen)  # pregressi jobs salvati ancora validi
            # print("old_jobs_list pre", old_jobs_list)

            # Aggiorna date e jobs
            if 'start_date' in form.changed_data \
                    or 'end_date' in form.changed_data \
                    or 'jobs' in form.changed_data:

                # Cancella i vecchi jobs eliminati dal form, se presenti in DateBook
                jobs_to_delete = sb.datebook_set.all().exclude(job__in=jobs_choosen)
                jobs_to_delete.delete()

                # Cancella le vecchie date eliminati dal form, se presenti in DateBook
                dates_to_delete = sb.datebook_set.all().exclude(date__in=new_range_dates_list)
                dates_to_delete.delete()

                # Aggiunge nuovi jobs alle date del FORM
                self._addJobs(new_range_dates_list, new_jobs_list)

                # Aggiunge le nuove date ai vecchi jobs
                self._addJobs(new_add_dates_list, old_jobs_list)

        # Salva le nuove scelte di SessionBook e DateBook (quest'ultimo per i valori del formset inline_formset)
        self.object = form.save()
        dates_form.instance = self.object
        dates_form.save()

        # Crea i messaggi di sistema
        if form.has_changed():
            messages.add_message(self.request, messages.SUCCESS,
                                 _(mark_safe("Session ID:{} <b>{}</b> have just been modified.".format(self.object.id, self.object))))
        if dates_form.has_changed():
            messages.add_message(self.request, messages.SUCCESS,
                                 _(mark_safe("Dates have just been modified.".format())))

        if self.request.POST.get("save_modify", False):
            return HttpResponseRedirect("")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, dates_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        # print("companies.SessionBookUpdateView.form_invalid")
        return self.render_to_response(
            self.get_context_data(form=form,
                                  dates_form=dates_form,
                                  ))

    def _addJobs(self, dates, jobs):
        """
        Funzione che aggiunge job e date al DateBook
        :param dates: list date type
        :param jobs: list instance Job
        """
        # print("companies.views.SessionBookUpdateView._addJobs")
        sb = self.object
        for job in jobs:
            for day in dates:
                db = DateBook(session=sb, job=job, date=day)
                db.save()



    def get_success_url(self):
        return reverse_lazy("companies:sessionbook-list")


@method_decorator(login_required, name='dispatch')
class SessionBookDeleteView(DeleteView):
    model = SessionBook
    success_url = reverse_lazy('companies:sessionbook-list')


# Gestione Self Booking Utente invitato. Vedi TMPL account/session_detail.html
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

        if self.pk:  # pk passato nella URL <int:pk> in automatico alla classe
            # Utente invitato, ma senza aver declinato l'invito
            ws = self.model.objects.filter(
                                            pk=self.pk,
                                            uuid=uuid,
                                            # expire_date__gte=now,
                                            user_option_list=request.user,
                                            ).exclude(user_decline_list=request.user).distinct()
            if ws:
                return ws[0]
            messages.add_message(request, messages.ERROR,
                                 mark_safe(_('Work session request <b>id {}</b>. '
                                             'You are not in list or you have '
                                             'been declined invitation.'.format(self.pk))))
        else:
            # Utente non presente in lista invito, oppure ha declinato, oppure parametri ricerca errati
            messages.add_message(request, messages.WARNING,
                             mark_safe(_('Request without result')))
        return self.model.objects.none()

    def get(self, request, pk):
        # print("companies.views.SessionBookDetailView.get")
        self.pk = pk
        obj = self.get_session_object(request=request)
        if obj:
            # user ha visto l'invito
            form = SessionBookDetailForm(instance=obj)

            u = self.request.user
            ps = SessionPrice.objects.get_or_create(session=obj, user=u)
            price = SessionPriceForm(user=u, instance=ps[0])

            return render(request, self.template_name,
                          {
                              'object': obj,
                              'form': form,
                              'priceform': price,
                          })
        return HttpResponseRedirect(reverse_lazy("account:index"))

    def post(self, request, pk):
        # print("companies.views.SessionBookDetailView.post")
        # print(request.POST)
        self.pk = pk  # id SessionBook
        obj = self.get_session_object(request=request)

        # u = self.request.user
        # ps = SessionPrice.objects.get_or_create(session=obj, user=u)[0]
        # price = SessionPriceForm(user=u, instance=ps)
        # price.instance.user = u
        # if u.id not in obj.confirmed_users():
        #     price = SessionPriceForm(data=request.POST, user=u, instance=ps)
        #     price.instance.sessione = obj
        #     price.save()

        # Data di prenotazione valida
        if not obj.is_expired():
            # Utente prenota alcune date
            if request.POST.get("response", "").lower() == "yes":
                date_ids = request.POST.getlist("date_id", [])

                # prenota solo le nuove date escludendo le date gi?? prenotate
                # todo: creare un metodo di classe per obj.datebook_set.filter (SessionBook)
                for date in obj.datebook_set.filter(id__in=date_ids).exclude(users=request.user):
                    date.user_book_add(request.user)
                    date.save()
                    messages.add_message(request, messages.SUCCESS,
                                         mark_safe(_('You have booked the date <b>{}</b>'.format(date.date))))
                    # inserisce OPZIONE in agenda utente
                    request.user.agenda_add_book(date)

                # rimuove le date gi?? prenotate che non trova nella lista dal form
                for date in obj.datebook_set.filter(users=request.user).exclude(id__in=date_ids):
                    date.user_book_remove(request.user)
                    date.save()
                    messages.add_message(request, messages.WARNING,
                                     mark_safe(_('You have removed the booked date <b>{}</b>'.format(date.date))))
                    # rimuove OPZIONE in agenda utente
                    request.user.agenda_remove_book(date)

                # todo: notifica alla company la modifica di prenotazione

                # Aggiorna le note
                for d in obj.datebook_set.all():
                    if d.job in request.user.jobprofile.job.all():
                        d.user_note = self.request.POST.get("user_note_{}".format(d.id))
                        d.save()

                form = SessionBookDetailForm(instance=obj)
                return render(request, self.template_name,
                              {
                                  'object': obj,
                                  'form': form,
                                  # 'priceform': price,
                              })

            # Utente declina l'invito. Non ha successiva possibilit?? di prenotare
            elif request.POST.get("response", "").lower() == "decline":
                # Viene aggiunto alla lista dei declinati
                obj.user_decline_list_add(request.user)
                # obj.save()
                # request.user.agenda_remove_book(date)
            return HttpResponseRedirect(reverse_lazy("account:index"))

        # Data di prenotazione scaduta oppure obj non trovato (obj is none)
        else:
            messages.add_message(request, messages.ERROR,
                                 mark_safe(_("Session is expired or some error occurred in request. "
                                             "Can't modify anythings")))
        return render(request, self.template_name, {'object': obj, 'priceform': price,})

    # def get_context_data(self, *args, **kwargs):
    #     context = super(SessionBookDetailView, self).get_context_data(*args, **kwargs)
    #     context['form'] = SessionBookDetailView()
    #     return context


# Gestione Comfirm utenti prenotati
@login_required(login_url="/account/login/")
def sessionBookUsers(request, pk):
    """Gestione Comfirm utenti prenotati"""
    # print("companies.views.sessionBookUsers")
    company_id = request.session.get("company_id")
    sb = SessionBook.objects.get(pk=pk, company__id=company_id)
    sb_form = SessionBookDetailForm(instance=sb)
    if request.POST:
        datebook_id = request.POST.get("datebook_id")
        users = request.POST.getlist("users")
        users_confirm = request.POST.getlist("users_confirm")

        db = DateBook.objects.get(pk=datebook_id)

        # aggiunge un utente dalla lista confermati della DateBook db
        if users:
            for user_id in users:
                u = User.objects.get(pk=user_id)
                if db.users_confirm.count() < db.number_user:
                    # todo: controllo se lo stesso utente ?? stato confermato nella stessa data (per altro job)
                    user_already_confirmed = sb.datebook_set.filter(date=db.date, users_confirm=u)
                    # print(user_already_confirmed)
                    if user_already_confirmed:
                        messages.add_message(request, messages.WARNING,
                                             _(mark_safe("!!! Operator <b>{}</b> is already confirmed as <b>{}</b> on <b>{}</b>"
                                                         "".format(u.getFullName,
                                                                   [x.job.title for x in user_already_confirmed],
                                                                   db.date))))
                    db.users_confirm.add(u)
                else:
                    messages.add_message(request, messages.ERROR,
                                         _(mark_safe("Operators <b>{}</b> are fully booked for the dates <b>{}</b>"
                                                     "".format(db.job.title, db.date))))
                # todo: notifica all'utente la conferma

        # rimuove un utente dalla lista confermati della DateBook db
        if users_confirm:
            for user_id in users_confirm:
                u = User.objects.get(pk=user_id)
                db.users_confirm.remove(u)
                # todo: notifica all'utente la rimozione dalla conferma
        db.save()
    return render(request, "companies/sessionbook_users.html", context={
        'sb': sb,
        'sb_form': sb_form,
    })


# * FUNZIONI PER MAP * #


@login_required(login_url="/account/login/")
def openMap(request, session_id=None):
    # print("companies.views.openMap")
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
            if timezone.now() > sb.expire_date:
                messages.add_message(request, messages.ERROR,
                                     _(mark_safe("Your Work Session is expired on <b>{}</b>".format(sb.expire_date))))
                return HttpResponseRedirect(reverse_lazy("companies:sessionbook-list"))
            context.update(company=c)
            context.update(sessionbook=sb)
            context.update(jobs=[x.title for x in sb.jobs.all()])
            context.update(initial_date_start="{}-{:02d}-{:02d}".format(sb.start_date.year,
                                                                        sb.start_date.month, sb.start_date.day))
            context.update(initial_date_end="{}-{:02d}-{:02d}".format(sb.end_date.year,
                                                                      sb.end_date.month, sb.end_date.day))
            context.update(qs_results=qs_results)

            # urls
            context.update(favoriteuser_url=reverse('companies:favoriteuser'))  # add/remove favorite user
            context.update(optionlist_url=reverse('companies:optionusers',
                                                  args=[session_id]))  # add/remove option list user
            context.update(retrive_optionlist_url=reverse('companies:retriveoptionlist',
                                                          args=[session_id]))  # add/remove option list user
            context.update(user_job_info_url=reverse('job:user-job-info'))
            # url per la ricerca dei markers jobprofile AGENDA sulla mappa
            context.update(api_markers_agenda_url="/maps/api/agendafree/")
            context.update(api_markers_agenda_url2="/maps/api/agendafree2/")
            # url per la ricerca dei markers jobprofile AGENDA BUSY sulla mappa
            context.update(api_markers_agendabusy_url="/maps/api/agendabusy/")
            context.update(api_markers_agendabusy_url2="/maps/api/agendabusy2/")
            # url per la ricerca dei markers DEFAULT POSITION sulla mappa
            context.update(api_markers_defaultposition_url="/maps/api/defaultposition/")
            context.update(api_markers_defaultposition_url2="/maps/api/defaultposition2/")
            context.update(api_search_job_url="/maps/api/search_job/")  # url per la ricerca dei markers sulla mappa
            return render(request, "companies/openmap.html", context)
    return redirect("account:index")


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
    Aggiunte/Toglie dalla lista 'list_users_from_map' in SessionBook
    un utente visualizzato sulla mappa.
    Per rimuovere usa il metodo sicuro 'user_option_list_secure_remove'.
    :return JSON bool True if add in list, False if remove from list
    """
    # print("companies.views.list_users_from_map")
    company_id = request.session.get("company_id", 1)
    sessionbook = SessionBook.objects.get(id=session_id, company__id=company_id)
    user_id = request.GET.get("user_id")
    u = User.objects.get(id=user_id)

    if sessionbook.invited_user(user_id):
        # prima di rimuovere dalla lista, controllare se non ?? nelle liste opzione/conferma
        res = sessionbook.user_option_list_secure_remove(u)
        if res == True:
            # print("rimosso")
            option_list = False
        else:
            option_list = res
    else:
        # print("aggiunto")
        option_list = sessionbook.user_option_list_add(u)
    # print(option_list)
    return JsonResponse({'option': option_list})


@login_required(login_url="/account/login/")
def retrive_users_from_map(request, session_id):
    """Render Template della lista di utenti selezionati dalla mappa"""
    # print("companies.views.retrive_users_from_map")
    company_id = request.session.get("company_id")
    sb = SessionBook.objects.get(id=session_id, company__id=company_id)
    listusers_obj = sb.user_option_list.all()
    if request.GET.get("json"):
        l_users = [
            {
                'user': x.getFullName,
                'id': x.id,
                'jobs': [y.title for y in x.jobprofile.job.all()],
                'booked': x.id in x.sessionbook_set.get(pk=sb.id).booked_users(),
            } for x in listusers_obj]
        # print(l_users)
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
