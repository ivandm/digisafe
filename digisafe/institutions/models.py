from django.db import models
from django.conf import settings
from django.core.files.storage import Storage, FileSystemStorage
from django.utils.translation import gettext as _

from courses.models import Courses
from centers.models import Center

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
    

class InstitutionFileSystemStorage(FileSystemStorage):
    def _save(self, name, content):
        # print("ProtocolFileSystemStorage._save name", name)
        file_root, file_ext = os.path.splitext(name)
        name = self.get_alternative_name(file_root, file_ext)
        # print("ProtocolFileSystemStorage._save name", name)
        return super()._save(name, content)
    
    def delete(self, name):
        print("InstitutionFileSystemStorage.delete name", name)
        super().delete(name)


fs = InstitutionFileSystemStorage(location='static/imgs/', base_url="/imgs")
class Institution(models.Model):
    admin   = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                        blank=True, null=True,
                    )
    name    = models.CharField(max_length=255, blank=True, default='')
    logo    = models.FileField(upload_to=file_path_name_institution, 
                               storage=fs, blank=True,
                               validators=[validate_file_size, validate_file_extension],
                              )
    use_custom_files = models.BooleanField(default=False, verbose_name=_("Use custom registry files"))
    centers = models.ManyToManyField(
                        Center,
                        blank=True,
                        related_name="associate_institutions"
                    )
    def __str__(self):
        return self.name
        
    def get_logo_url(self):
        if self.logo:
            return static(self.logo.url)
        else:
            return None


def validate_customfile_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf']
    if not ext.lower() in valid_extensions:
        raise ValidationError(_("Unsupported file extension. Valid extetions are '{0}'".format(".pdf")))

def customfile_path_name_institution(instance, file_name):
    file_root, file_ext = os.path.splitext(file_name)
    return "file_inst_{}_{}_{}".format(instance.institution.id, instance.name.replace(' ', '-').lower(), file_ext)


fsCustomFiles = InstitutionFileSystemStorage(location='files/', base_url="/document")
class InstitutionCustomFiles(models.Model):
    "Files specifici dell'Ente"
    institution = models.ForeignKey(
            Institution,
            on_delete=models.CASCADE,
        )
    name = models.CharField(max_length=255, blank=False, default='')
    file = models.FileField(upload_to=customfile_path_name_institution,
                               storage=fsCustomFiles, blank=False,
                               validators=[validate_file_size, validate_customfile_extension],
                              )
    need = models.BooleanField(default=False, help_text=_("Check that if this file is mandatory"))
    description = models.TextField(default='', blank=True)

    def __str__(self):
        return "{0}".format(self.name)

    def delete(self, *args, **kwargs):
        print("InstitutioCustomFiles delete")
        self.file.delete() # obbligato per cancellare il file nel filesystem
        super().delete(*args, **kwargs)


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