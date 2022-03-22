from django.urls import path, include

from .views import accountView, logoutView, loginView, loginLostView, \
    changePasswordView, resetPasswordView, setPosition, certificateView, \
    dissociateCompanyView, searchCourseView, calendarView, CalendarDelEventView, \
    CalendarFormEventView


urlpatterns = [
    path('', accountView, name="index"),
    path('company/<int:pk>/dissociate/', dissociateCompanyView, name="dissociate"),
    path('login/', loginView, name="login"),
    path('logout/', logoutView, name="logout"),
    path('loginlost/', loginLostView, name="login-lost"),
    path('changepassword/', changePasswordView, name="change-password"),
    path('resetpassword/', resetPasswordView, name="reset-password"),
    path('user/setposition', setPosition, name="setposition"),
    path('protocol/<int:pk_protocol>/view/', certificateView, name="view-certificate"),
    path('searchcourse/', searchCourseView, name="searchcourse"),
    path('agenda/view/', calendarView, name="calendar"),
    path('agenda/set/<int:year>/<int:month>/', calendarView, name="calendar-set"),
    path('agenda/add/<slug:year>/<slug:month>/<slug:day>/', calendarView, name="calendar-add"),
    path('agenda/edit/<int:pk>/year/<int:year>/<int:month>/<int:day>/',
         CalendarFormEventView.as_view(), name="calendar-edit"),
    path('agenda/del/<int:pk>/', CalendarDelEventView.as_view(), name="calendar-del"),

]