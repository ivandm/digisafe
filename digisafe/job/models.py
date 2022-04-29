from django.db import models


class UpperCaseCharField(models.CharField):

    def __init__(self, *args, **kwargs):
        super(UpperCaseCharField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        if value:
            value = value.upper()
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(UpperCaseCharField, self).pre_save(model_instance, add)


class Job(models.Model):
    code = UpperCaseCharField(max_length=50, default="", unique=True)
    title = models.CharField(max_length=255, default="", unique=True)
    description = models.TextField(max_length=1000, default="", blank=True)

    def __str__(self):
        return "{} [{}]".format(self.title, self.code)
