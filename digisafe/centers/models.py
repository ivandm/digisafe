from django.db import models
from django.conf import settings
from django.templatetags.static import static

from courses.models import Courses

### Manage files ### 
import os
from django.core.exceptions import ValidationError
def validate_file_size(value):
    filesize= value.size
    if filesize > 2097152: #2MB
        raise ValidationError(_("The maximum file size that can be uploaded is {0}".format("2MB")))
    else:
        return value
     
def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.png', '.jpeg', '.jpg']
    if not ext.lower() in valid_extensions:
        raise ValidationError(_("Unsupported file extension. Valid extension are '{0}'".format(".png .jpg .jpeg")))
        
def file_path_name_center(instance, file_name):
    file_root, file_ext = os.path.splitext(file_name)
    return "logo_center_{0}_{1}".format(instance.id, file_ext)
    
from django.core.files.storage import Storage, FileSystemStorage
class ProtocolFileSystemStorage(FileSystemStorage):
    def _save(self, name, content):
        # print("ProtocolFileSystemStorage._save name", name)
        file_root, file_ext = os.path.splitext(name)
        name = self.get_alternative_name(file_root, file_ext)
        # print("ProtocolFileSystemStorage._save name", name)
        return super()._save(name, content)
    
    def delete(self, name):
        # print("ProtocolFileSystemStorage.delete name", name)
        super().delete(name)
        
fs = ProtocolFileSystemStorage(location='static/imgs/', base_url="/imgs")

class Center(models.Model):
    name     = models.CharField(max_length=255, blank=True, default='')
    director = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                        blank=True, null=True,
                    )
    logo    = models.FileField(upload_to=file_path_name_center, 
                               storage=fs, blank=True,
                               validators=[validate_file_size, validate_file_extension],
                              )
    staff   = models.ManyToManyField(
                        settings.AUTH_USER_MODEL,
                        blank=True,
                        related_name="associate_staff"
                    )
    trainers = models.ManyToManyField(
                        settings.AUTH_USER_MODEL,
                        blank=True,
                        related_name="associate_centers"
                    )
    def __str__(self):
        return self.name
    
    def get_logo_url(self):
        if self.logo:
            return static(self.logo.url)
        else:
            return ""

    def sendEmailDirector(self, subject='', msg=''):
        # print("model Center")
        print(self.director.sendSystemEmail(subject, msg))

    def sendEmailStaff(self, subject='', msg=''):
        # print("model Center")
        for u in self.staff.all():
            print(u.sendSystemEmail(subject, msg))


class CoursesAdmitedCenter(models.Model):
    """Corsi gestiti"""
    center = models.OneToOneField(
            Center,
            on_delete=models.CASCADE,
        )
    courses = models.ManyToManyField(
                Courses,
                blank=True,
                help_text="Corsi gestiti"
            )
    note = models.TextField(default='', blank=True)

    def __str__(self):
        return "{}".format(self.center)