from django.db import models

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
        raise ValidationError(_("Unsupported file extension. Valid extetions are '{0}'".format(".png .jpg .jpeg")))
           
def file_path_name_institution(instance, file_name):
    file_root, file_ext = os.path.splitext(file_name)
    return "logo_inst_{0}_{1}".format(instance.id, file_ext)
    
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

class Institution(models.Model):
    name    = models.CharField(max_length=255, blank=True, default='')
    logo    = models.FileField(upload_to=file_path_name_institution, 
                               storage=fs, blank=True,
                               validators=[validate_file_size, validate_file_extension],
                              )
    def __str__(self):
        return self.name
        
    def get_logo_url(self):
        if self.logo:
            return static(self.logo.url)
        else:
            return None
        
class CoursesAdmitedInstitution(models.Model):
    """Corsi gestiti"""
    institution = models.OneToOneField(
            Institution,
            on_delete=models.CASCADE,
        )
    courses = models.ManyToManyField(
                Courses,
                blank=True,
                help_text="Corsi gestiti"
            )
    note = models.TextField(default='', blank=True)