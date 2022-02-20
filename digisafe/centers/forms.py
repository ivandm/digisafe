from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import Center


class CenterForm(forms.ModelForm):
    class Meta:
        model = Center
        fields = "__all__"

    def clean(self):
        if self.instance:
            cleaned_data = super().clean()
            director = cleaned_data.get("director")
            # if director:
                # print("CenterlForm.clean instance", self.instance)
                # print("CenterlForm.clean director", director.id, director)
                # print("CenterlForm.clean director's center", director.trainingcenter.centers.filter(pk=self.instance.id))
                # if not director.trainingcenter.centers.filter(pk=self.instance.id):
                # if not self.instance.director == director:
                #     raise ValidationError(
                #             _('User director %(user)s in not associate with this center. Please associate one first.'),
                #             code='invalid',
                #             params={'user': "{0} {1}".format(director.first_name,director.last_name) },
                #         )
        pass
                