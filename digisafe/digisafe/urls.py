"""digisafe URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from protocol.views import ProtocolAutocompleteJsonView, protocol_download_file, protocol_download_sign_file
from users.views import CheckExistObjJsonView

urlpatterns = [
    path('', include(('home.urls', 'home'), namespace='home')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('account/', include(('account.urls', 'account'), namespace='account')),
    path('accounts/', include(('account.urls', 'accounts'), namespace='accounts')),
    path('company/', include(('companies.urls', 'companies'), namespace='companies')),
    path('institutions/', include(('institutions.urls', 'institutions'), namespace='institutions')),
    path('maps/', include(('maps.urls', 'maps'), namespace='maps')),
    path('jobs/', include(('job.urls', 'job'), namespace='job')),
    path('pricelist/', include(('pricelist.urls', 'job'), namespace='pricelist')),

    path('admin/autocomplete_check_field/', CheckExistObjJsonView.as_view()), #completamento automatico del campo
    path('admin/', admin.site.urls),

    path('tinymce/', include('tinymce.urls')),  # WYSIWYG editor

    path('countries/', include('countries.urls')),
    path('protocol/', include('protocol.urls')),
    path('document/<str:path>/', protocol_download_file, name="protocol-download-file"),
    path('signs/<str:path>/', protocol_download_sign_file, name="protocol-sign-file"),

] + static("/imgs/", document_root=settings.STATIC_ROOT / "imgs")

handler404 = 'home.views.custom_page_not_found_view'
handler500 = 'home.views.custom_error_view'
handler403 = 'home.views.custom_permission_denied_view'
handler400 = 'home.views.custom_bad_request_view'

