from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError

import os
import io
from PIL import ImageFile as PillowImageFile

from countries.models import Country, City
from courses.models import Courses
from institutions.models import Institution
from job.models import Job

# Costanti usate qui
SIGN_MAX_SIZE = (500, 250)  # in pixels


class User(AbstractUser):
    description = models.TextField(default='', blank=True)
    owner = models.ForeignKey(
                            settings.AUTH_USER_MODEL,
                            on_delete=models.CASCADE,
                        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def __str__(self):
        try:
            fiscal_code = self.anagrafica.fiscal_code
        except:
            fiscal_code = ""
        if self.first_name or self.last_name:
            return "{last_name} {first_name} - {fiscal_code}".format(
                            first_name=self.first_name,
                            last_name=self.last_name,
                            fiscal_code=fiscal_code)
        return "{utente} - {fiscal_code}".format(utente=self.username,
                                                 fiscal_code=fiscal_code)
    
    def fiscal_code(self):
        return self.anagrafica.fiscal_code

    @property
    def getFullName(self):
        return "{0} {1}".format(self.last_name, self.first_name)

    def getFullNameInverse(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def sendSystemEmail(self, subject, msg):
        send_mail(
            subject,
            msg,
            None,  # 'from@example.com',
            [self.email],
            fail_silently=False,
        )


class Anagrafica(models.Model):
    user = models.OneToOneField(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    )
    birthday = models.DateField(null=True, blank=True)
    country = models.ForeignKey(
                        Country,
                        on_delete=models.CASCADE,
                        null=True, blank=True
                    )
    city = models.ForeignKey(
                        City,
                        on_delete=models.CASCADE,
                        null=True, blank=True
                    )
    fiscal_code = models.CharField(max_length=255, unique=True, blank=False, null=False)
        
    def __str__(self):
        utente = self.user
        if self.user.first_name or self.user.last_name:
            utente = "{last_name} {first_name} {cf}".format(
                            first_name=self.user.first_name,
                            last_name=self.user.last_name, 
                            cf=self.fiscal_code)
        
        return "Anagrafica di {utente} ".format(utente=utente)
    
    def getPlaceTemplate(self):
        return "{0} {1}".format(self.city, self.birthday)


# ## Manage files ## #


def validate_file_trasparence(value):
    p = PillowImageFile.Parser()
    if hasattr(value.file, 'read'):
        file = value.file
        file_pos = file.tell()
        file.seek(file_pos)
        data = file.read()
        p.feed(data)
        x, y = p.image.size
        if x > SIGN_MAX_SIZE[0] or y > SIGN_MAX_SIZE[1]:
            raise ValidationError(_("Max size is {0}x{1}px (w,h). You try load image size of {2}x{3}px"
                                    .format(SIGN_MAX_SIZE[0], SIGN_MAX_SIZE[1], x, y)))
        if not hasattr(p.image, 'png'):
            raise ValidationError(_("Your sign file needs trasparency in background. "
                                    "We have not check it. Your file should be in .png with transparent."))
    return value


def validate_file_size(value):
    filesize = value.size
    if filesize > 500000:  # 500KB
        raise ValidationError(_("The maximum file size that can be uploaded is {0}".format("0.5MB/500KB")))
    else:
        return value


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.png']
    if not ext.lower() in valid_extensions:
        raise ValidationError(_("Unsupported file extension. Valid extetion is '{0}'".format(".png")))


def file_path_name(instance, file_name):
    file_root, file_ext = os.path.splitext(file_name)
    return "sign_{0}_{1}_{2}".format(instance.user.id, instance.user.last_name, file_ext)


class ProtocolFileSystemStorage(FileSystemStorage):
    def _save(self, name, content):
        # print("ProtocolFileSystemStorage._save name", name)
        # file_root, file_ext = os.path.splitext(name)
        # name = self.get_alternative_name(file_root, file_ext)
        # print("ProtocolFileSystemStorage._save name", name)
        return super()._save(name, content)
    
    def delete(self, name):
        # print("ProtocolFileSystemStorage.delete name", name)
        super().delete(name)
    
    def signFile(self, name, data=None):
        file_root, file_ext = os.path.splitext(name)
        signedFilePath = file_root+"_signed"+file_ext
        if self.exists(signedFilePath):
            print("exist", signedFilePath)
            master = signedFilePath
        else:
            master = name
        self.drawSigns(master, signedFilePath, data)
        
    def getSignedFileName(self, name):
        # name: deve essere sempre il file originale
        if not name or type(name) != type(""):
            return False
        print("ProtocolFileSystemStorage.getSigned", name)
        file_root, file_ext = os.path.splitext(name)
        signedFile = file_root+"_signed"+file_ext
        if self.exists(signedFile):
            return signedFile
        return name
        
    def drawSigns(self, signFile, destFile, data):
        """

        :type signFile: il file che deve essere firmato
                  se esiste una versione firmata prende quest'ultima
                  altrimenti usa la versione originale da firmare
        :type destFile: il file con le firme messe
        :type data: data
        """
        signFile_tmp = self.path(signFile+".tmp")
        destFile = self.path(destFile)
        # print ("ProtocolFileSystemStorage.drawSigns")
        # print ("signFile", signFile)
        # print ("destFile", destFile)
        # print ("signFile_tmp", signFile_tmp)
        if self.exists(signFile_tmp):
            print("Processo bloccato. File tmp esistente. Attendere la fine del processo in corso")
            return False
        shutil.copyfile(self.path(signFile), self.path(signFile_tmp))
        # read your existing PDF
        sign_file = open(signFile_tmp, "rb")
        existing_pdf = PdfFileReader(sign_file)
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page

        for pag in range(data["num_pages"]):
            # print()
            # print("pagina: ", pag+1)
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            if data["signs"].get(str(pag+1), False):
                for item in data["signs"][str(pag+1)]:
                    # print(item["pdfcoord"])
                    c = item["pdfcoord"]
                    # print(c[0], c[1])
                    can.drawString(c[0], c[1], "Hello world")        
            else:
                can.drawString(0, 0, "")
            can.save()

            # move to the beginning of the StringIO buffer
            packet.seek(0)

            # create a new PDF with Reportlab
            new_pdf = PdfFileReader(packet)
            
            page = existing_pdf.getPage(pag)
            page.mergePage(new_pdf.getPage(0))
            output.addPage(page)
        # finally, write "output" to a real file
        outputStream = open(destFile, "wb")
        output.write(outputStream)
        outputStream.close()
        sign_file.close()
        
        # Rimuove la copia del file 
        os.remove(self.path(signFile_tmp))


fs = ProtocolFileSystemStorage(location='signs/', base_url="/signs")


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    institution = models.BooleanField(default=False)
    administrator = models.BooleanField(default=False)
    director = models.BooleanField(default=False)
    trainer = models.BooleanField(default=False)
    sign = models.ImageField(
        upload_to=file_path_name,
        storage=fs, blank=True,
        validators=[validate_file_size, validate_file_extension, validate_file_trasparence],
        # help_text="file help text",
    )

    def __str__(self):
        if self.user.first_name or self.user.last_name:
            return "Profile of " + "{last_name} {first_name}".format(
                            first_name=self.user.first_name,
                            last_name=self.user.last_name)
        return "Profile of " + "{utente}".format(utente=self.user)


class JobProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    job = models.ManyToManyField(
        Job,
        blank=True,
        help_text=_("Jobs")
    )

    def __str__(self):
        return "{}".format(self.user)


class Subjects(models.Model):
    """Materie di docenza"""
    user = models.OneToOneField(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name="materie"
        )
    subjects = models.ManyToManyField(
                Courses,
                blank=True,
                help_text=_("Permitted courses")
            )
    note = models.TextField(default='', blank=True)
    
    class Meta:
        pass
        
    def __str__(self):
        return "{last_name} {first_name}'s subjects ".format(
                                                        last_name=self.user.last_name, 
                                                        first_name=self.user.first_name)
                                                        

class Institutions(models.Model):
    """Enti esterni associati"""
    
    user = models.OneToOneField(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            # related_name = "centers"
        )
    institutions = models.ManyToManyField(
                Institution,
                blank=True,
                help_text="Enti associati"
            )
    note = models.TextField(default='', blank=True)
    
    class Meta:
        pass
        
    def __str__(self):
        return "{last_name} {first_name} ".format(
                                                        last_name=self.user.last_name, 
                                                        first_name=self.user.first_name)
                                                        
