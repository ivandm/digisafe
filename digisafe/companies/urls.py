from django.urls import path, include

from .views import companyDetailView, companyPublicDetailView, requestAssociateToUser, requestAssociateToCompany
from .views import requestAssociateAction, retrieve_users_to_associate, requestDissociateAction

urlpatterns = [
    path('<int:pk>/view/', companyDetailView, name="company-view"),
    path('<int:pk>/public/view/', companyPublicDetailView, name="company-public-view"),
    path('associateuser/', requestAssociateToUser, name="company-request-user"),
    path('<int:pk>/dissociateuseraction/', requestDissociateAction, name="company-dissociate-user"),
    path('associateuseraction/', requestAssociateAction, name="company-request-user-action"),
    path('associatecompany/', requestAssociateToCompany, name="user-request-company"),
    path('users/search/', retrieve_users_to_associate, name="company-user-search"),

]