from django.shortcuts import render, redirect
from django.urls import reverse

def home(request):
    if request.user.is_authenticated:
        return redirect(reverse("account:index"))
    return render(request, "home/index.html")
