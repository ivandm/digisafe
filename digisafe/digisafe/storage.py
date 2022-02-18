### Manage files ###
import os
from django.core.exceptions import ValidationError


def validate_file_size(value):
    max_size = 2097152
    filesize = value.size
    if filesize > max_size:  # 2MB
        raise ValidationError(_("The maximum file size that can be uploaded is {0}".format("2MB")))
    else:
        return value


def validate_file_extension_img(value):
    valid_extensions = ['.png', '.jpeg', '.jpg']
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    #valid_extensions = ['.png', '.jpeg', '.jpg']
    if not ext.lower() in valid_extensions:
        raise ValidationError(_("Unsupported file extension. Valid extetions are '{0}'".format(".png .jpg .jpeg")))


def file_path_name_center(instance, file_name):
    prefix = "file"
    file_root, file_ext = os.path.splitext(file_name)
    return "{}_{}_{}".format(prefix, instance.id, file_ext)


from django.core.files.storage import Storage, FileSystemStorage as FS
class FileSystemStorage(FS):
    def _save(self, name, content):
        # print("ProtocolFileSystemStorage._save name", name)
        file_root, file_ext = os.path.splitext(name)
        name = self.get_alternative_name(file_root, file_ext)
        # print("ProtocolFileSystemStorage._save name", name)
        return super()._save(name, content)

    def delete(self, name):
        # print("ProtocolFileSystemStorage.delete name", name)
        super().delete(name)

# esempio di utilizzo:
#       fs = FileSystemStorage(location='static/imgs/', base_url="/imgs")
#
# nel modello:
#       logo    = models.FileField(upload_to=file_path_name_center,
#                    storage=fs, validators=[validate_file_size, validate_file_extension],
#                   )