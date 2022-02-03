from django.contrib import admin


class DigiSafeAdminSite(admin.AdminSite):
    site_header = 'IRCoT Digital Safety administration'
    site_title  = 'Digi.Safe. site admin'


    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        # urls += [
            # path('<str:app_name>/<int:pk>/actions/', ActionListView.as_view(), name='actions-list'),
        # ]
        return urls
        
    