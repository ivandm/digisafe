from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from users.models import User
from courses.models import Courses
from .models import Session, Learners, Protocol, Files
from countries.models import Country
from countries.forms import ChainedCountryForm
from .widgets import AdminFileSignWidget

class ProtocolForm(forms.ModelForm):
    
    class Meta:
        model = Protocol
        fields = "__all__"
        # widgets = {
            # 'course': AutocompleteSelect(),
        # }
    
    def clean(self):
        if self.instance:
            cleaned_data = super().clean()
            course = cleaned_data.get("course")
            if course:
                learners = cleaned_data.get("learners_request")
                typecourse = cleaned_data.get("type")
                maxlearnsers = getattr(Courses.objects.get(pk=course.id), typecourse).max_learners_theory
                # print("ProtocolForm.clean", learners, maxlearnsers)
                if int(learners) > maxlearnsers or int(learners) < 0:
                    raise ValidationError(
                            _('Learnser number error: Max admited is %(learners)s (Min is 0).'),
                            code='invalid',
                            params={'learners': maxlearnsers},
                        )


class SessionForm(ChainedCountryForm):

    class Meta:
        model = Session
        fields = "__all__"
        
    def clean(self):
        # print("SessionForm.clean", self.instance)
        if self.instance:
            cleaned_data = super().clean()
            date = cleaned_data.get("date")
            trainer = cleaned_data.get("trainer")
            start_time = cleaned_data.get("start_time")
            end_time = cleaned_data.get("end_time")
            if trainer in [x for x in self.instance.protocol.getLearners()]:
                raise ValidationError(
                    _('Invalid user: %(user)s. The user is a learner.'),
                    code='invalid',
                    params={'user': trainer},
                )
            if end_time and start_time:
                "Ora finale deve essere maggiorne di ora iniziale"
                if end_time < start_time:
                    raise ValidationError(
                        _('Invalid time: End time %(end_time)s is lower than start time %(start_time)s.'),
                        code='invalid',
                        params={'end_time': end_time.strftime("%H:%M"), 'start_time': start_time.strftime("%H:%M")},
                    )
                if self.instance.getDateTimeRange(trainer, date, start_time, end_time):
                    raise ValidationError(
                        _('Invalid date for user: %(user)s. The user is busy on %(date)s from %(start_time)s and %(end_time)s.'),
                        code='invalid',
                        params={'user': trainer, 'date': date, 'start_time':start_time.strftime("%H:%M"), 'end_time':end_time.strftime("%H:%M")},
                    )
                if self.instance.getTheoryTimes(date, start_time, end_time):
                    # print("SessionForm.clean", start_time, end_time)
                    raise ValidationError(
                        _('Invalid time for date: %(date)s. The time from %(start_time)s and %(end_time)s is busy on theory session.'),
                        code='invalid',
                        params={'date': date, 'start_time':start_time.strftime("%H:%M"), 'end_time':end_time.strftime("%H:%M")},
                    )


class LearnersForm(forms.ModelForm):
   
    def __init__(self, *args, **kwargs):
        super(LearnersForm, self).__init__(*args, **kwargs)
        # if self.instance:
            # self.fields['user'].queryset = \
                # User.objects.all().order_by('last_name')
        pass
        
    class Meta:
        model = Learners
        fields = "__all__"
        
    def clean(self):
        # print("LearnersForm.clean")
        if self.instance:
            cleaned_data = super().clean()

            upload    = cleaned_data.get("inst_cert")
            import os
            if upload == False and self.instance.inst_cert:
                # cancella il file associato quando si spunta il checkbox 'clear'
                if os.path.os.path.lexists(self.instance.inst_cert.path):
                    # cancella solo il file se esiste
                    # print("Cancella file")
                    self.instance.inst_cert.delete(False)
                    pass
            
            learner   = cleaned_data.get("user")
            if self.instance.isBusy(learner):
                raise ValidationError(
                    _('User busy: %(user)s. The user is busies in other course on these date and time session.'),
                    code='invalid',
                    params={'user': learner},
                )
            if learner in [x for x in self.instance.protocol.getTrainers()]:
                raise ValidationError(
                    _('Invalid user: %(user)s. The user is a trainer.'),
                    code='invalid',
                    params={'user': learner},
                )
            
            # self.instance.save()
            pass
    

class IntegrationInfoForm(forms.Form):
    info = forms.CharField(widget=forms.Textarea, help_text=_("Write in the box to text integration information message"))


class DeniedConfirmForm(forms.Form):
    info_denied = forms.CharField(widget=forms.Textarea, help_text=_("Without fill this form doesn't chage the status in case of denied choise"))


class FilesForm(forms.ModelForm):
    
    class Meta:
        model = Files
        fields = "__all__"
        widgets = {
            'file': forms.ClearableFileInput(attrs={"target": "blank_", "class": "boh"})
           }
        pass
    