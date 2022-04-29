from django.urls import path, include

from .views import job_user_info

urlpatterns = [
    path('userjobinfo/', job_user_info, name="user-job-info"),
]