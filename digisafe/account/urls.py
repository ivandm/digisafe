from django.urls import path, include

from .views import accountView, logoutView, loginView, loginLostView, changePasswordView, resetPasswordView, setPosition



urlpatterns = [
    path('', accountView, name="index"),
    path('login/', loginView, name="login"),
    path('logout/', logoutView, name="logout"),
    path('loginlost/', loginLostView, name="login-lost"),
    path('changepassword/', changePasswordView, name="change-password"),
    path('resetpassword/', resetPasswordView, name="reset-password"),
    path('user/setposition', setPosition, name="setposition"),

]