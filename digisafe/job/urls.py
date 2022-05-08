from django.urls import path, include

from .views import job_user_info, index

urlpatterns = [
    path('<int:pk>/info/', index, name="info"),
    path('userjobinfo/', job_user_info, name="user-job-info"),
]