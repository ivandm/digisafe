from django.shortcuts import render, redirect
from django.urls import reverse

def home(request):
    if request.user.is_authenticated:
        return redirect(reverse("account:index"))
    return render(request, "home/index.html")

def custom_page_not_found_view(request, exception):
    return render(request, "home/errors/404.html", {})

def custom_error_view(request, exception=None):
    return render(request, "home/errors/500.html", {})

def custom_permission_denied_view(request, exception=None):
    return render(request, "home/errors/403.html", {})

def custom_bad_request_view(request, exception=None):
    return render(request, "home/errors/400.html", {})