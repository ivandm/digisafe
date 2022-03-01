from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.utils.translation import gettext as _
from django.db.models import Q

from users.models import User
from account.models import UsersPosition
from .models import Company, requestAssociatePending

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
            qs_results = UsersPosition.objects.filter(user__associates_company=c)
            request.session["company_id"] = pk
            context.update(company=c)
            context.update(qs_results=qs_results)
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
    action     = request.POST.get("action") # accept/refuse
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
    user_id    = request.POST.get("user_id")
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
        if u == request.user: # utente chiede associazione a company
            r = requestAssociatePending(user=u, company=c, user_req=True)
        else:
            r = requestAssociatePending(user=u, company=c, company_req=True)
        r.save()
        return JsonResponse({'save': 'ok'})
    return JsonResponse({})