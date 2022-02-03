from django.urls import path

from .views import city_list

urlpatterns = [
    path('country/<int:country_id>', city_list),
]