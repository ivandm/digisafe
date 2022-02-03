from django.contrib.admin.apps import AdminConfig

class DigiSafeAdminSite(AdminConfig):
    default_site = 'digisafe.admin.DigiSafeAdminSite'