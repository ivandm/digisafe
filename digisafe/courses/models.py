from django.db import models
from django.conf import settings
from django import forms
from django.utils.translation import gettext as _

from tinymce.models import HTMLField
import datetime

from utils.time import *
from countries.models import Country


class DurationFieldForm(forms.DurationField):
    # widget = myTextInput
    def to_python(self, value):
        "Dal form all'oggetto python"
        # print("DurationFieldForm.to_python", value, type(value))
        value = "%s:00:00"%value
        return super().to_python(value)
        
    def prepare_value(self, value):
        "Dall'oggetto python al valore visualizzato nel form"
        # print("DurationFieldForm.prepare_value",value)
        if isinstance(value, datetime.timedelta):
            h,m = timedelta_to_hm(value)
            return "%s"%h
        return value


class DurationField(models.DurationField):
    def formfield(self, **kwargs):
        return super().formfield(**{
            'form_class': DurationFieldForm,
            **kwargs,
        })
    

class Courses(models.Model):
    code    = models.CharField(max_length=255, default='', unique=True)
    country = models.ManyToManyField(
                Country,
                blank=True,
                help_text="Stati permessi"
            )
    active  = models.BooleanField(default=True)
    need_institution  = models.BooleanField(default=False)
     
    class Meta:
        verbose_name_plural = "courses"
        
    def __str__(self):
        return "{title} - {code} {country} Ore:{ore}".format(code=self.code, 
                                                    title=self.feature.title, 
                                                    country=[x.code for x in self.country.all()],
                                                    ore=self.tot_ore(),
                                                    )
    
    def id(self):
        return self.pk
        
    def feature_title(self):
        return self.feature.title
    
    def country_code(self):
        return [x.code for x in self.country.all()]
    
    def tot_ore(self):
        ht,mt=timedelta_to_hm(self.new.theory)
        hp,mp=timedelta_to_hm(self.new.practice)
        return ht+hp


class Feature(models.Model):
    course  = models.OneToOneField(
                Courses,
                on_delete=models.CASCADE,
            )
    title   = models.CharField(max_length=255, blank=True, default='')
    desc    = models.TextField(default='', blank=True)
    laws    = models.TextField(default='', blank=True)
    years   = models.IntegerField(default=5, blank=True)
    notes   = models.TextField(default='', blank=True)
    RISK_CHOICES = [
        ("L", _('Low')),
        ("M", _('Medium')),
        ("H", _('Higth')),
        ]
    risk = models.CharField(
                    max_length=1,
                    choices=RISK_CHOICES,
                    default="L",
                )
    contents = models.ManyToManyField(
                "ContentCourse",
                blank=True,
            )
    
    class Meta:
        verbose_name_plural = "features"
        
    def __str__(self):
        return "{title} ({code})".format(title=self.title, code=self.course.code)


class New(models.Model):
    course                  = models.OneToOneField(
                                Courses,
                                on_delete=models.CASCADE,
                            )
    theory                  = DurationField(default=0)
    practice                = DurationField(default=0)
    max_learners_theory     = models.IntegerField(default=0, help_text=_("Per course"))
    max_learners_practice   = models.IntegerField(default=0, help_text=_("Per trainer"))

    class Meta:
        verbose_name_plural = "New"
        
    def __str__(self):
        return "New {course}".format(course=self.course.feature.title)

    def _prepare_value(self, value):
        value = self.theory
        if isinstance(value, datetime.timedelta):
            h,m = timedelta_to_hm(value)
            return "%s"%h
        return value
        
    def theory_html(self):
        return self. _prepare_value(self.theory)
    
    def practice_html(self):
        return self. _prepare_value(self.practice)
    
    
class Update(models.Model):
    course                  = models.OneToOneField(
                                Courses,
                                on_delete=models.CASCADE,
                            )
    year                    = models.IntegerField(default=0)
    theory                  = DurationField(default=0)
    practice                = DurationField(default=0)
    max_learners_theory     = models.IntegerField(default=0, help_text=_("Per course"))
    max_learners_practice   = models.IntegerField(default=0, help_text=_("Per trainer"))
    
    class Meta:
        verbose_name_plural = "Update"
        
    def __str__(self):
        return "Update {course}".format(course=self.course.feature.title)
    
    def _prepare_value(self, value):
        value = self.theory
        if isinstance(value, datetime.timedelta):
            h,m = timedelta_to_hm(value)
            return "%s"%h
        return value
        
    def theory_html(self):
        return self. _prepare_value(self.theory)
    
    def practice_html(self):
        return self. _prepare_value(self.practice)


class ContentCourse(models.Model):
    course = models.ForeignKey(
                    Courses,
                    on_delete=models.CASCADE,
                )
    i18 = models.CharField(max_length=5, blank=False, default='')
    content = HTMLField()
    
    class Meta:
        unique_together = ('course', 'i18',)
        
    def __str__(self):
        return "{0} [{1}]".format(self.course.feature.title, self.i18)