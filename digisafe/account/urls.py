from django.urls import path, include

from .views import accountView, logoutView, loginView, loginLostView, \
    changePasswordView, resetPasswordView, setPosition, certificateView, \
    dissociateCompanyView, searchCourseView, calendarView, CalendarDelEventView, \
    CalendarFormEventView, CalendarAddView, coursesView, indexView, SettingsView


urlpatterns = [
    path('', indexView, name="index"),
    path('courses/', coursesView, name="courses"),
    path('settings/<int:pk>/', SettingsView.as_view(), name="settings"),
    path('agenda/view/', calendarView, name="calendar"),
    path('agenda/set/<int:year>/<int:month>/', calendarView, name="calendar-set"),
    path('agenda/add/<int:year>/<int:month>/<int:day>/', CalendarAddView.as_view(), name="calendar-add"),
    path('agenda/edit/<int:pk>/date/<int:year>/<int:month>/<int:day>/',
         CalendarFormEventView.as_view(), name="calendar-edit"),
    path('agenda/del/<int:pk>/', CalendarDelEventView.as_view(), name="calendar-del"),

    path('company/<int:pk>/dissociate/', dissociateCompanyView, name="dissociate"),
    path('login/', loginView, name="login"),
    path('logout/', logoutView, name="logout"),
    path('loginlost/', loginLostView, name="login-lost"),
    path('changepassword/', changePasswordView, name="change-password"),
    path('resetpassword/', resetPasswordView, name="reset-password"),
    path('user/setposition', setPosition, name="setposition"),
    path('protocol/<int:pk_protocol>/view/', certificateView, name="view-certificate"),
    path('searchcourse/', searchCourseView, name="searchcourse"),


]