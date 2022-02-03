from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout,authenticate, login
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.mail import EmailMessage, BadHeaderError
from django.contrib import messages
from django.http import JsonResponse

from .forms import AccountAuthenticationForm, AccountLoginLostForm, AccountChangePasswordForm, AccountResetPasswordForm
from .models import TmpPassword, UsersPosition
from companies.models import requestAssociatePending, Company
from users.models import User

@login_required(login_url="/account/login/")
def accountView(request):
    context = {
        'pending': request.user.requestassociatepending_set.filter(user_req=False),
    }
    if request.user.profile.administrator:
        c = Company.objects.filter(admins=request.user)
        p = UsersPosition.objects.filter(user = request.user)
        if p:
            context.update(position=p[0])
        print("accountView", c)
        context.update(company_list=c)
    return render(request, "account/index.html", context=context)
    
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

def logoutView(request):
    logout(request)
    return redirect(reverse('home:index'))

def loginLostView(request):
    if request.method == 'POST':
        form = AccountLoginLostForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            u = User.objects.filter(email=email)
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
                    from_email='from@example.com',
                    reply_to=('from@example.com',),
                    to=[email],
                ).send(fail_silently=False)
                return redirect(reverse('account:reset-password'))
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
                    from_email='from@example.com',
                    reply_to=('from@example.com',),
                    to=[email],
                ).send(fail_silently=False)
                return redirect(reverse('account:login'))
            except BadHeaderError:
                return HttpResponse(_('Invalid header found.'))
        return render(request, "account/reset_password.html", context={'form':form})
    form = AccountResetPasswordForm()
    return render(request, "account/reset_password.html", context={'form':form})
    
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
                    from_email='from@example.com',
                    reply_to=('from@example.com',),
                    to=[email],
                ).send(fail_silently=False)
            except BadHeaderError:
                return HttpResponse(_('Invalid header found.'))
        return redirect(reverse('account:login'))
    else:
        form = AccountChangePasswordForm()
        return render(request, "account/change_password.html", context={'form':form})

def setPosition(request):
    lat=request.POST.get("lat")
    lon=request.POST.get("lon")
    user = request.user
    if lat and lon:
        pos = UsersPosition.objects.get(user=request.user)
        pos.setGeom(lon, lat)
        pos.save()
        return JsonResponse({'save': True})
    return JsonResponse({'save': False})