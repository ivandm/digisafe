from django.contrib import admin

from .models import Job
from .forms import JobForm

@admin.register(Job)
class CenterAdmin(admin.ModelAdmin):
    form = JobForm

    class Media:
        css = {
            'all': (
                'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
                'css/admin_bootstrap_correct.css',
            )
        }
        js = (
            'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js',
        )
