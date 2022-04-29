from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

import datetime

from courses.models import Courses
from .models import Session, Learners, Protocol, Files
from countries.forms import ChainedCountryForm


class ProtocolForm(forms.ModelForm):
    
    class Meta:
        model = Protocol
        fields = "__all__"
    
    def clean(self):
        if self.instance:
            cleaned_data = super().clean()
            course = cleaned_data.get("course")
            center = cleaned_data.get("center")
            institution = cleaned_data.get("institution")
            if course:
                learners = cleaned_data.get("learners_request")
                typecourse = cleaned_data.get("type")
                maxlearnsers = getattr(Courses.objects.get(pk=course.id), typecourse).max_learners_theory
                # print("ProtocolForm.clean", learners, maxlearnsers)
                if int(learners) > maxlearnsers or int(learners) < 0:
                    raise ValidationError(
                            _('Learner number error: Max admitted is %(learners)s (Min is 0).'),
                            code='invalid',
                            params={'learners': maxlearnsers},
                        )
            if course:
                if course.need_institution and institution:
                    if not center:
                        raise ValidationError(
                            _('Center is mandatory'),
                            code='invalid',
                            # params={'learners': maxlearnsers},
                        )
                    print(institution, type(institution))
                    print(center.associate_institutions.filter(pk=institution.id))


class SessionForm(ChainedCountryForm):

    def __init__(self, *args, **kwargs):
        # print("SessionForm")
        super(SessionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Session
        fields = "__all__"
        
    def clean(self):
        # print("SessionForm.clean")

        if self.instance:
            cleaned_data = super().clean()
            date = cleaned_data.get("date")
            init_date = self.get_initial_for_field(self.fields['date'], 'date')
            # print(self.get_initial_for_field(self.fields['date'], 'date'))
            # print(self.fields['date'].has_changed(init_date,date))
            # print()
            trainer = cleaned_data.get("trainer")
            start_time = cleaned_data.get("start_time")
            end_time = cleaned_data.get("end_time")
            if trainer in [x for x in self.instance.protocol.getLearners()]:
                raise ValidationError(
                    _('Invalid user: %(user)s. The user is a learner.'),
                    code='invalid',
                    params={'user': trainer},
                )
            if self.instance.protocol.course.need_institution \
                    and self.fields['date'].has_changed(init_date, date) \
                    and self.instance.protocol.is_authorized():
                if not self.instance.isPreDate(date):
                    pre_days = self.instance.protocol.institution.pre_days
                    today = datetime.date.today()
                    end_date = today + datetime.timedelta(days=pre_days)
                    raise ValidationError(
                        _('Invalid date: Cannot insert request before %(date)s or change '
                          'date if the course has been authorized'),
                        code='invalid',
                        params={'date': end_date},
                    )
            if end_time and start_time:
                "Ora finale deve essere maggiore di ora iniziale"
                if end_time < start_time:
                    raise ValidationError(
                        _('Invalid time: End time %(end_time)s is lower than start time %(start_time)s.'),
                        code='invalid',
                        params={'end_time': end_time.strftime("%H:%M"), 'start_time': start_time.strftime("%H:%M")},
                    )
                if self.instance.getDateTimeRange(trainer, date, start_time, end_time):
                    raise ValidationError(
                        _('Invalid date for user: %(user)s. The user is busy on '
                          '%(date)s from %(start_time)s and %(end_time)s.'),
                        code='invalid',
                        params={'user': trainer, 'date': date, 'start_time': start_time.strftime("%H:%M"),
                                'end_time': end_time.strftime("%H:%M")},
                    )
                if self.instance.getTheoryTimes(date, start_time, end_time):
                    # print("SessionForm.clean", start_time, end_time)
                    raise ValidationError(
                        _('Invalid time for date: %(date)s. The time from %(start_time)s '
                          'and %(end_time)s is busy on theory session.'),
                        code='invalid',
                        params={'date': date, 'start_time': start_time.strftime("%H:%M"),
                                'end_time': end_time.strftime("%H:%M")},
                    )


class LearnersForm(forms.ModelForm):
   
    def __init__(self, *args, **kwargs):
        super(LearnersForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Learners
        fields = "__all__"
        
    def clean(self):
        # print("LearnersForm.clean")
        if self.instance:
            cleaned_data = super().clean()

            upload = cleaned_data.get("inst_cert")
            import os
            if upload is False and self.instance.inst_cert:
                # cancella il file associato quando si spunta il checkbox 'clear'
                if os.path.lexists(self.instance.inst_cert.path):
                    # cancella solo il file se esiste
                    # print("Cancella file")
                    self.instance.inst_cert.delete(False)
                    pass
            
            learner = cleaned_data.get("user")
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
    info = forms.CharField(
        widget=forms.Textarea,
        help_text=_("Write in the box to text integration information message"))


class DeniedConfirmForm(forms.Form):
    info_denied = forms.CharField(
        widget=forms.Textarea,
        help_text=_("Without fill this form doesn't change the status in case of denied choice"))


class FilesForm(forms.ModelForm):
    
    class Meta:
        model = Files
        fields = "__all__"
        widgets = {
            'file': forms.ClearableFileInput(attrs={"target": "blank_", "class": "boh"})
           }
        pass
    