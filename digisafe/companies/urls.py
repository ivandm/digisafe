from django.urls import path, include

from .views import home, set_company
from .views import companyDetailView, companyPublicDetailView, requestAssociateToUser, requestAssociateToCompany
from .views import requestAssociateAction, retrieve_users_to_associate, requestDissociateAction
from .views import favoriteuser, list_users_from_map, retrive_users_from_map, book_user
from .views import SessionBookCreateView, SessionBookListView, SessionBookUpdateView, SessionBookDetailView,\
                    SessionBookDeleteView, openMap, send_invite_now, SettingsCompanyView

urlpatterns = [
    path('home/', home, name="home"),
    path('<int:pk>/set/', set_company, name="set-company"),
    path('settings/', SettingsCompanyView.as_view(), name="setting"),

    path('<int:pk>/view/', companyDetailView, name="company-view"),
    path('<int:pk>/public/view/', companyPublicDetailView, name="company-public-view"),
    path('associateuser/', requestAssociateToUser, name="company-request-user"),
    path('<int:pk>/dissociateuseraction/', requestDissociateAction, name="company-dissociate-user"),
    path('associateuseraction/', requestAssociateAction, name="company-request-user-action"),
    path('associatecompany/', requestAssociateToCompany, name="user-request-company"),
    path('users/search/', retrieve_users_to_associate, name="company-user-search"),

    path('openmap/book/<int:session_id>/view/', openMap, name="openmap"),
    path('openmap/book/<int:session_id>/optionlist/', list_users_from_map, name="optionusers"),
    path('openmap/book/<int:session_id>/retriveoptionlist/', retrive_users_from_map, name="retriveoptionlist"),
    path('openmap/book/<int:session_id>/invite/', send_invite_now, name="send-invite"),

    path('favoriteuser/', favoriteuser, name="favoriteuser"),
    path('bookuser/', book_user, name="bookuser"),


    path('sessionbook/list/', SessionBookListView.as_view(), name="sessionbook-list"),
    path('sessionbook/create/', SessionBookCreateView.as_view(), name="sessionbook-create"),
    path('sessionbook/<int:pk>/update/', SessionBookUpdateView.as_view(), name="sessionbook-update"),
    path('sessionbook/<int:pk>/delete/', SessionBookDeleteView.as_view(), name="sessionbook-delete"),
    # path('sessionbook/<int:pk>/detail/', SessionBookDetailView.as_view(), name="sessionbook-detail"),
    path('sessionbook/<int:pk>/bookresponse/', SessionBookDetailView.as_view(), name="sessionbook-bookresponse"),

]
