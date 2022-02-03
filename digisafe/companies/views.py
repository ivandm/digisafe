from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.utils.translation import gettext as _
from django.db.models import Q

from users.models import User
from account.models import UsersPosition
from .models import Company, requestAssociatePending

def companyDetailView(request, pk=None):
    # print("companyDetailView")
    context = {}
    if pk:
        c = Company.objects.get(pk=pk)
        # print(c.associates.all())
        qs_results = UsersPosition.objects.all()
        request.session["company_id"] = pk
        context.update(company=c)
        context.update(qs_results=qs_results)
    return render(request, "companies/index.html", context)

def retrieve_users_to_associate(request):
        print("retrieve_users_to_associate.retrieve", request)
        slug = request.POST.get('slug')
        company_id = request.session.get("company_id")
        if company_id and slug:
            c = Company.objects.get(pk=company_id)
            print(c.associates.all())
            user_list = User.objects.filter( 
                                             Q(last_name__icontains=slug) | Q(first_name__icontains=slug)
                                            ).exclude(id__in=c.associates.all())
            print(user_list)
            return render(request, template_name='companies/get_user_list_detail.html', context={'object_list': user_list})
        raise Http404(_("No users matches the given query."))
        
def companyPublicDetailView(request, pk=None):
    context = {}
    if pk:
        c = Company.objects.get(pk=pk)
        request.session["company_id"] = pk
        context.update(company=c)
    return render(request, "companies/public_view.html", context)

def requestAssociateAction(request):
    request_id = request.POST.get("request_id")
    action     = request.POST.get("action") # accept/refuse
    if request_id:
        r = requestAssociatePending.objects.get(pk=request_id)
        c = r.company
        u = r.user
        if action == "accept":
            c.associates.add(u)
            r.delete()
            return JsonResponse({'accept': 'ok'})
        elif action == "refuse":
            r.delete()
            return JsonResponse({'refuse': 'ok'})

    return JsonResponse({'nothing': 'ok'})
    
def requestAssociateToUser(request):
    # Company chiede associazione ad un utente
    user_id = request.GET.get("user_id")
    company_id = request.session.get("company_id")
    if user_id and company_id:
        u = User.objects.get(pk=user_id)
        c = Company.objects.get(pk=company_id)
        r = requestAssociatePending(user=u, company=c, company_req=True)
        r.save()
        return JsonResponse({'save': 'ok'})
    return JsonResponse({})
    
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