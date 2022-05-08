from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import redirect, get_object_or_404

from users.models import User
from .models import Job

@login_required(login_url="/account/login/")
def index(request, pk):
    job = Job.objects.get(pk=pk)
    return render(request, 'job/index.html', context={'job': job})


@login_required(login_url="/account/login/")
def job_user_info(request):
    user_id = request.GET.get("user_id")
    json = request.GET.get("json")
    if user_id and json:
        jobs = [x.title for x in User.objects.get(id=user_id).jobprofile.job.all()]

        return JsonResponse({'jobs': jobs})
    return redirect('home:index')
