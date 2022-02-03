from django.urls import path, include

from .views import registerView, examView, protocol_user_check, sign_file, save_signs, remove_signs

app_name = "protocol"
urlpatterns = [
    path('register/<int:pk>/view/', registerView, name='register-view'),
    path('exam/<int:pk>/view/', examView, name='exam-reporter-view'),
    path('<int:protocol_pk>/user/<int:user_pk>/check/', protocol_user_check, name='protocol-user-check'),
    path('file/<int:file_pk>/sign/', sign_file, name='protocol-sign-file'),
    path('savepdf/', save_signs, name='protocol-save-signs'),
    path('removeSignsPdf/', remove_signs, name='protocol-remove-signs'),

]