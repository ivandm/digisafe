from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout, authenticate, login
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.mail import EmailMessage, BadHeaderError
from django.contrib import messages
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.db.models import Q
from django.views.generic.edit import FormView, CreateView, DeleteView, UpdateView

import datetime

from .forms import AccountAuthenticationForm, AccountLoginLostForm, AccountChangePasswordForm, \
    AccountResetPasswordForm, CalendarFormEvent
from .models import TmpPassword, UsersPosition
from companies.models import requestAssociatePending, Company
from users.models import User
from protocol.models import Protocol

@login_required(login_url="/account/login/")
def accountView(request):
    context = {
        'agendas': UsersPosition.objects.filter(user=request.user),
        'pending': request.user.requestassociatepending_set.filter(user_req=False),
        'companies': request.user.associates_company.filter(active=True).order_by("name").values("id", "name")
    }
    if request.user.profile.administrator:
        c = Company.objects.filter(admins=request.user)
        p = UsersPosition.objects.filter(user = request.user)
        if p:
            context.update(position=p[0])
        # print("accountView", c)
        context.update(company_list=c)
    if request.user.learners_set.count():
        context.update(courses=request.user.learners_set.all().order_by('-protocol__course__id'))
    return render(request, "account/index.html", context=context)


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
    return TemplateResponse(request, "calendar/index.html", context)


class CalendarFormEventView(UpdateView):
    model = UsersPosition
    form_class = CalendarFormEvent
    context_object_name = 'item'
    template_name = 'account/calendar_event_form.html'
    # fields = ['anonymous', 'date_start', 'date_end', 'object', 'description']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        print("CalendarFormEventView.dispatch")
        self.item_id = kwargs['pk']
        self.year = kwargs['year']
        self.month = kwargs['month']
        self.day = kwargs['day']
        print(args, kwargs)
        return super(CalendarFormEventView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        print("CalendarFormEventView.get_context_data")
        context = super(CalendarFormEventView, self).get_context_data(*args, **kwargs)
        context['year'] = self.year
        context['month'] = self.month
        context['day'] = self.day
        return context

    def form_valid(self, form):
        # print("CalendarFormEventView.form_valid")
        form.save()
        item = UsersPosition.objects.get(pk=self.item_id)
        # print(item)
        # print(item.date_start.year)
        return redirect(reverse('account:calendar', args=[item.date_start.year, item.date_start.month]))


class CalendarDelEventView(DeleteView):
    model = UsersPosition
    template = "account/usersposition_confirm_delete.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        print("CalendarDelEventView.dispatch")
        print(args, kwargs)
        return super(CalendarDelEventView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, user, *args, **kwargs):
        print("CalendarDelEventView.form_valid")
        print(args, kwargs)
        print(user)
        print(self.object)

        # self.item_id = kwargs['pk']
        # self.year = 0
        # self.month = 0
        # return super(CalendarDelEventView, self).form_valid(user, *args, **kwargs)

    def get_success_url(self):
        return redirect(reverse('account:index'))
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

def loginView(request):
    if request.method == 'POST':
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('account:index'))
            else:
                # Return an 'invalid login' error message.
                return render(request, "account/login.html", 
                              context={
                                        'error_login':_("Invalid username or password."),
                                        'form':form})
    form = AccountAuthenticationForm()
    return render(request, "account/login.html", context={'form':form})

@login_required(login_url="/account/login/")
def logoutView(request):
    logout(request)
    return redirect(reverse('home:index'))

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
                mex = "Username: {0}<br>Auth code: {1}<br>link: {2}".format(u.username, t.cod_auth, reverse('account:reset-password'))
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
        return render(request, "account/lost_login.html", context={'form':form})

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
            mex = "Your password has been changed<br>"
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
        return render(request, "account/reset_password.html", context={'form':form})
    form = AccountResetPasswordForm()
    return render(request, "account/reset_password.html", context={'form':form})

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
        pos, created = UsersPosition.objects.get_or_create(user=request.user)
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