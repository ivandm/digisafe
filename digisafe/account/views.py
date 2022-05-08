from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout, authenticate, login
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.core.mail import EmailMessage, BadHeaderError
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.db.models import Q
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from django.utils import timezone

import datetime

from agenda.models import Agenda
from companies.models import requestAssociatePending, Company, SessionBook
from users.models import User
from protocol.models import Protocol
from .forms import AccountAuthenticationForm, AccountLoginLostForm, AccountChangePasswordForm, \
    AccountResetPasswordForm, CalendarFormEvent
from .forms import AccountForm, AnagraficaFormSet, AgendaFeaturesFormSet
from .models import TmpPassword


@login_required(login_url="/account/login/")
def indexView(request):
    return render(request, "account/index.html", context={})


@login_required(login_url="/account/login/")
def coursesView(request):
    context = {}
    if request.user.learners_set.count():
        context.update(courses=request.user.learners_set.all().order_by('-protocol__course__id'))
    return render(request, "account/home_courses.html", context=context)


@method_decorator(login_required, name='dispatch')
class SettingsView(UpdateView):
    template_name = "account/settings.html"
    form_class = AccountForm
    model = User

    def get_context_data(self, **kwargs):
        data = super(SettingsView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['form'] = AccountForm(self.request.POST, instance=self.object)
            data['anagrafica'] = AnagraficaFormSet(self.request.POST, instance=self.object)
            data['agendafeatures'] = AgendaFeaturesFormSet(self.request.POST, instance=self.object)
        else:
            data['form'] = AccountForm(instance=self.object)
            data['anagrafica'] = AnagraficaFormSet(instance=self.object)
            data['agendafeatures'] = AgendaFeaturesFormSet(instance=self.object)
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
        anagrafica_form = AnagraficaFormSet(self.request.POST, instance=self.object)
        agendadefaultposition_form = AgendaFeaturesFormSet(self.request.POST, instance=self.object)
        if form.is_valid() and anagrafica_form.is_valid():
            return self.form_valid(form, anagrafica_form, agendadefaultposition_form)
        else:
            return self.form_invalid(form, anagrafica_form, agendadefaultposition_form)

    def form_valid(self, form, anagrafica_form, agendadefaultposition_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        self.object = form.save()
        anagrafica_form.instance = self.object
        anagrafica_form.save()
        agendadefaultposition_form.instance = self.object
        agendadefaultposition_form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, anagrafica_form, agendadefaultposition_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form,
                                  anagrafica=anagrafica_form,
                                  agendafeatures=agendadefaultposition_form
                                  ))

    def get_success_url(self):
        return reverse_lazy("account:settings", args=[self.object.id])


@login_required(login_url="/account/login/")
def calendarView(request, *args, **kwargs):
    # print("account.views.agenda")
    # print(args)
    # print(kwargs)
    context = {}
    today = datetime.datetime.today()
    context.update(today=today)
    context.update(year=kwargs.get('year', today.year))
    context.update(month=kwargs.get('month', today.month))
    return TemplateResponse(request, "account/agenda.html", context)


@method_decorator(login_required, name='dispatch')
class CalendarAddView(CreateView):
    model = Agenda
    form_class = CalendarFormEvent
    # fields = "__all__"

    def get_success_url(self):
        return reverse('account:calendar-set', args=[self.year, self.month])

    def dispatch(self, *args, **kwargs):
        # print("CalendarAddView.dispatch")
        # print(args, kwargs)
        self.year = kwargs.get('year')
        self.month = kwargs.get('month')
        self.day = kwargs.get('day')
        hour = timezone.now().hour
        min = timezone.now().minute
        self.date_start = datetime.datetime(self.year, self.month, self.day, hour, min)
        self.user = self.request.user
        return super(CalendarAddView, self).dispatch(*args, **kwargs)

    def get_initial(self):
        return {
            'date_start': self.date_start,
        }

    def form_valid(self, form):
        # print("CalendarAddView.form_valid ")

        # Validation Busy in the Date Range Form
        s_date = form.cleaned_data['date_start']
        e_date = form.cleaned_data['date_end']
        events = self.request.user.agenda_set.filter(
            (Q(date_start__lte=e_date) & Q(date_end__gte=e_date)) |
            (Q(date_start__lte=s_date) & Q(date_end__gte=s_date))
        )
        # se ci sono date impegnate nel range indicato, non salva.
        if events:
            messages.add_message(self.request, messages.ERROR, _('You are busy in that date range.'))
            form.add_error(None, _('You are busy in that date range.'))
            form.add_error("date_start", _('You are busy in that date range.'))
            form.add_error("date_end", _('You are busy in that date range.'))
            return self.render_to_response(
                self.get_context_data(form=form,
                                      ))

        # Every dates are ok. User are not busy
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        # do something with self.object
        # remember the import: from django.http import HttpResponseRedirect
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        # print("CalendarFormEventView.get_context_data")
        context = super(CalendarAddView, self).get_context_data(*args, **kwargs)
        context['year'] = self.year
        context['month'] = self.month
        context['day'] = self.day
        return context


@method_decorator(csrf_protect, name='dispatch')
class CalendarFormEventView(UpdateView):
    model = Agenda
    form_class = CalendarFormEvent
    context_object_name = 'item'
    # template_name = 'account/calendar_event_form.html'
    # fields = ['anonymous', 'date_start', 'date_end', 'object', 'description']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # print("CalendarFormEventView.dispatch")
        self.item_id = kwargs['pk']
        self.year = kwargs['year']
        self.month = kwargs['month']
        self.day = kwargs['day']
        # print(args, kwargs)
        return super(CalendarFormEventView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('account:calendar-set', args=[self.year, self.month])

    def get_context_data(self, *args, **kwargs):
        # print("CalendarFormEventView.get_context_data")
        context = super(CalendarFormEventView, self).get_context_data(*args, **kwargs)
        context['year'] = self.year
        context['month'] = self.month
        context['day'] = self.day
        return context

    def form_valid(self, form):
        # print("CalendarFormEventView.form_valid")

        # Validation Busy in the Date Range Form
        s_date = form.cleaned_data['date_start']
        e_date = form.cleaned_data['date_end']
        events = self.request.user.agenda_set.filter(
            (Q(date_start__lte=e_date) & Q(date_end__gte=e_date)) |
            (Q(date_start__lte=s_date) & Q(date_end__gte=s_date))
        ).exclude(pk=self.object.pk)
        # se ci sono date impegnate nel range indicato, non salva.
        if events:
            messages.add_message(self.request, messages.ERROR, _('You are busy in that date range.'))
            form.add_error(None, _('You are busy in that date range.'))
            form.add_error("date_start", _('You are busy in that date range.'))
            form.add_error("date_end", _('You are busy in that date range.'))
            return self.render_to_response(
                self.get_context_data(form=form,
                                      ))

        # Every dates are ok. User are not busy
        form.save()
        return redirect(self.get_success_url())


@method_decorator(login_required, name='dispatch')
class CalendarDelEventView(DeleteView):
    model = Agenda
    template = "account/Agenda_confirm_delete.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        print("CalendarDelEventView.dispatch")
        print(args, kwargs)
        return super(CalendarDelEventView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        print("CalendarDelEventView.get_success_url")
        return reverse('account:index')
        # return redirect(reverse('account:calendar', args=[self.year, self.month]))


@login_required(login_url="/account/login/")
def searchCourseView(request):
    slug = request.POST.get("slug")
    print(slug)
    context = {}
    if request.user.learners_set.count() and slug:
        context.update(courses=request.user.learners_set.filter( \
            Q(protocol__course__feature__title__icontains=slug)\
            # Q(protocol__course__feature__title__icontains=slug) \
                ).order_by('-protocol__course__id'))
    else:
        context.update(courses=request.user.learners_set.all().order_by('-protocol__course__id'))
    return render(request, "account/home_courses_object.html", context=context)


@login_required(login_url="/account/login/")
def dissociateCompanyView(request, pk):
    # print(request.user.associates_company.filter(pk=pk))
    c = request.user.associates_company.filter(pk=pk)
    if c:
        c[0].associates.remove(request.user)
    return redirect(reverse('account:index'))


# Non inserire login_required
def loginView(request):
    if request.method == 'POST':
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if request.GET.get("next", False):
                    return redirect(request.GET.get("next"))
                return redirect(reverse('account:index'))
            else:
                # Return an 'invalid login' error message.
                return render(request, "account/login.html", 
                              context={
                                        'error_login':_("Invalid username or password."),
                                        'form':form})
    form = AccountAuthenticationForm()
    return render(request, "account/login.html", context={'form': form})


@login_required(login_url="/account/login/")
def logoutView(request):
    logout(request)
    return redirect(reverse('home:index'))


# Non inserire login_required
def loginLostView(request):
    if request.method == 'POST':
        form = AccountLoginLostForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            u = User.objects.filter(email=email)
            # u = get_object_or_404(User, email=email)
            if u: # se esite cambia crea la password temporanea
                u = u[0]
                t = TmpPassword(user=u)
                t.set_client_ip(request)
                t.save()
                
                # new_password = User.objects.make_random_password()
                # u.set_password(new_password)
                # u.save()# cambia la password all'utente
                
                messages.success(request, _('New auth code was sent to {0}.'.format(email)))
                messages.info(request, _('Check your email. Beware it\'s not in spam.'))
                # invia la nuova password per email
                mex = "Username: {0}\n\n" \
                      "Auth code: {1}\n\n" \
                      "link: {2}?auth_code={3}".format(
                            u.username,
                            t.cod_auth,
                            settings.HTTP+settings.CURRENT_SITE+reverse('account:reset-password'),
                            t.cod_auth,
                        )

                EmailMessage(
                    subject=_('Digi.Safe. new credentials'),
                    body=mex,
                    from_email='noreply@ircot.net',
                    reply_to=('noreply@ircot.net',),
                    to=[email],
                ).send(fail_silently=False)
                return redirect(reverse('account:reset-password'))
            else:
                messages.error(request, _('Email {0} doesn\'t check into database.'.format(email)))
                return render(request, "error_pages/email_404.html", context={'email': email})
    else:
        form = AccountLoginLostForm()
        return render(request, "account/lost_login.html", context={'form': form})


# Non inserire login_required
def resetPasswordView(request):
    if request.method == 'POST':
        form = AccountResetPasswordForm(request.POST)
        if form.is_valid():
            auth_code = form.cleaned_data['auth_code'].replace("-","")
            password = form.cleaned_data['password']
            t = TmpPassword.objects.get(cod_auth=auth_code)
            t.user.set_password(password)
            try:
                t = TmpPassword.objects.get(cod_auth=auth_code)
                t.user.set_password(password)
                t.user.save()# cambia la password all'utente
            except:
                messages.error(request, _('Error in request. Check your auth code and try again.'))
                return render(request, "account/reset_password.html", context={'form':form})
            messages.success(request, _('Password has been changed.'))
            email = t.user.email
            mex = "Your password has been changed\n\n"
            try:
                EmailMessage(
                    subject=_('Digi.Safe. new password'),
                    body=mex,
                    from_email='noreply@ircot.net',
                    reply_to=('noreply@ircot.net',),
                    to=[email],
                ).send(fail_silently=False)
                return redirect(reverse('account:login'))
            except BadHeaderError:
                return HttpResponse(_('Invalid header found.'))
        return render(request, "account/reset_password.html", context={'form': form})
    form = AccountResetPasswordForm(initial=request.GET)
    return render(request, "account/reset_password.html", context={'form': form})


@login_required(login_url="/account/login/")
def changePasswordView(request):
    if request.method == 'POST':
        form = AccountChangePasswordForm(request.POST)
        context = {'form': form}
        if form.is_valid():
            password = form.cleaned_data['password']
            u = request.user
            u.set_password(password)
            u.save()# cambia la password all'utente
            messages.success(request, _('Password has been changed.'))
            
            email = u.email
            mex = "Your password has been changed<br>"
            try:
                EmailMessage(
                    subject=_('Digi.Safe. new password'),
                    body=mex,
                    from_email='noreply@ircot.net',
                    reply_to=('noreply@ircot.net',),
                    to=[email],
                ).send(fail_silently=False)
            except BadHeaderError:
                return HttpResponse(_('Invalid header found.'))
        return redirect(reverse('account:login'))
    else:
        form = AccountChangePasswordForm()
        return render(request, "account/change_password.html", context={'form':form})


@login_required(login_url="/account/login/")
def setPosition(request):
    lat=request.POST.get("lat")
    lon=request.POST.get("lon")
    user = request.user
    if lat and lon:
        pos, created = Agenda.objects.get_or_create(user=request.user)
        pos.setGeom(lon, lat)
        pos.save()
        return JsonResponse({'save': True})
    return JsonResponse({'save': False})


@login_required(login_url="/account/login/")
def certificateView(request, pk_protocol=None, user_id=None):
        from utils.helper import qrcode_str2base64
        from django.contrib.sites.shortcuts import get_current_site
        # print("ProtocolAdmin.actions_view request",request)
        if not pk_protocol == None:
            protocol = Protocol.objects.get(pk=pk_protocol)
            trainer = request.user
            full_url = ''.join(
                ['http://', get_current_site(request).domain, "protocol/", str(protocol.id), "/user/", str(trainer.id),
                 "/check/"])

            # todo: implementazione del codice qr del certificato
            # if settings.DEBUG:
            #     full_url = ''.join(
            #         ['http://', "192.168.10.104:8000/", "protocol/", str(protocol.id), "/user/", str(trainer.id),
            #          "/check/"])
            # print("ProtocolAdmin.certificate_user full_url", full_url)

            context = dict(
                # Include common variables for rendering the admin template.
                #self.admin_site.each_context(request),
                # Anything else you want in the context...
                trainer=trainer,
                #opts=self.opts,
                protocol=protocol,
                #module_name=self.model._meta.model.__name__,
                #media=self.media,
                web_site="digisafe.ircot.co.uk",
                qrcode_img=qrcode_str2base64(full_url)
            )
        return TemplateResponse(request, "protocol/certificate_user.html", context)


@login_required(login_url="/account/login/")
def accountView(request):
    context = {
        'agendas': Agenda.objects.filter(user=request.user),
        'pending': request.user.requestassociatepending_set.filter(user_req=False),
        'companies': request.user.associates_company.filter(active=True).order_by("name").values("id", "name")
    }
    if request.user.profile.administrator:
        c = Company.objects.filter(admins=request.user)
        p = Agenda.objects.filter(user = request.user)
        if p:
            context.update(position=p[0])
        # print("accountView", c)
        context.update(company_list=c)
    if request.user.learners_set.count():
        context.update(courses=request.user.learners_set.all().order_by('-protocol__course__id'))
    return render(request, "account/index.html", context=context)


# BOOKING #

# todo: implementare la pagina dei works session
class WorkSessionView(ListView):
    model = SessionBook
    template_name = 'account/sessionbook_list.html'

    def get_queryset(self):
        # print("account.views.WorkSessionView.get_queryset")
        qs = SessionBook.objects.filter(user_option_list=self.request.user)
        # print(qs)
        return qs
