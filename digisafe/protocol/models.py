from django.db import models
from django.utils.translation import gettext as _
from django import forms
from django.forms.widgets import TextInput
from django.db.models import Q
from django.db.models import Sum, DurationField, ExpressionWrapper, F, IntegerField, Value

import math
import datetime
from utils import time

# from .widgets import FileSignField

from courses.models import Courses
from users.models import User
from countries.models import Country, City
from centers.models import Center
from institutions.models import Institution
from digisafe.storage import FileInstCertStorage

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
    valid_extensions = ['.pdf']
    if not ext.lower() in valid_extensions:
        raise ValidationError(_("Unsupported file extension. Valid extetions are '{0}'".format("pdf")))
        
def file_path_name(instance, file_name):
    file_root, file_ext = os.path.splitext(file_name)
    return "prot_{0}_{1}_{2}".format(instance.protocol.id, instance.doc_type, file_ext)
   
from django.core.files.storage import Storage, FileSystemStorage
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
import io, shutil

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
        signedName = self.checkSigned(name)
        if signedName:
            super().delete(signedName)
        
    def signFile(self, name, fileObj=None):
        file_root, file_ext = os.path.splitext(name)
        signedFilePath = file_root+"_signed"+file_ext
        # if self.exists(signedFilePath):
            # print("exist", signedFilePath)
            # master = signedFilePath
        # else:
            # master = name
        master = name
        self.drawSigns(master, signedFilePath, fileObj)
    
    def checkSigned(self, name):
        # ritorna il nome del file se esiste, altrimenti False
        file_root, file_ext = os.path.splitext(name)
        signedFile = file_root+"_signed"+file_ext
        if self.exists(signedFile):
            return signedFile
        return False
        
    def getSignedFileName(self, name):
     # name:  deve essere sempre il file originale
        if not name or type(name) != type(""):
            return False
        # print("ProtocolFileSystemStorage.getSigned", name)
        file_root, file_ext = os.path.splitext(name)
        signedFile = file_root+"_signed"+file_ext
        if self.exists(signedFile):
            return signedFile
        return name
        
    def drawSigns(self, signFile, destFile, fileObj):
        # signFile: il file che deve essere firmato
        #           se esiste una versione firmata prende quest'ultima
        #           altrimenti usa la versione originale da firmare
        # destFile: il file con le firme messe
        
        signFile_tmp = self.path(signFile+".tmp")
        destFile = self.path(destFile)
        # todo: bisogna migliorare il controllo del processo per evitare due richieste contemporanee
        if self.exists(signFile_tmp):
            print("Processo bloccato. File tmp esistente. Attendere la fine del processo in corso")
            # os.remove(self.path(signFile_tmp))
            return False
        shutil.copyfile(self.path(signFile), self.path(signFile_tmp))
        # read your existing PDF
        sign_file = open(signFile_tmp, "rb")
        existing_pdf = PdfFileReader(sign_file)
        output = PdfFileWriter()
        pages = existing_pdf.getNumPages()
        signs = Signs.objects.filter(file=fileObj).order_by("uiid")
        
        for pag in range(0, pages):
            page = existing_pdf.getPage(pag)
            
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            
            if signs.filter(page=pag+1):
                for sign in signs.filter(page=pag+1):
                    mask = [215,255,215,255,215,255] # elimina il bianco
                    # print(sign.user.profile.sign.path)
                    can.drawImage(sign.user.profile.sign.path, sign.pdf_x-50, sign.pdf_y-25, 100, 50, mask=mask, anchor="c", preserveAspectRatio =True)
                    can.drawCentredString (sign.pdf_x, sign.pdf_y, "%s %s"%(sign.user.first_name,sign.user.last_name) ) 
                    can.drawCentredString (sign.pdf_x, sign.pdf_y-14, "%s"%(sign.timestamp.strftime("%d-%m-%Y %H:%M")) ) 
                    
            else:
                can.drawString(0,0, "")
            can.save()
            #move to the beginning of the StringIO buffer
            packet.seek(0)
            # create a new PDF with Reportlab
            new_pdf = PdfFileReader(packet)
            page.mergePage(new_pdf.getPage(0))
            
            output.addPage(page)
        # finally, write "output" to a real file
        outputStream = open(destFile, "wb")
        output.write(outputStream)
        outputStream.close()
        sign_file.close()
        # Rimuove la copia del file 
        os.remove(self.path(signFile_tmp))
    
    def url(self, name):
        # Ritorna il file firmato se esiste
        # print("ProtocolFileSystemStorage.url")
        return super().url(self.getSignedFileName(name))
        
fs = ProtocolFileSystemStorage(location='files/', base_url="/document")
### END Manage files ###


class Protocol(models.Model):
    datetime   = models.DateTimeField(auto_now_add=True)
    owner      = models.ForeignKey(
                    User,
                    on_delete=models.CASCADE,
                    # editable=False,
                    )
    course     = models.ForeignKey(
                    Courses,
                    on_delete=models.CASCADE,
                )

    TYPE_CHOICES = [
        ("new", _('New')),
        ("update", _('Update')),
        ]
    type        = models.CharField(
                    max_length=25,
                    choices=TYPE_CHOICES,
                    default="new",
                )
    
    learners_request = models.IntegerField(default=0)
    STATUS_CHOICES = [
        ("m", 'Modifica'),
        ("r", 'Richiesta'),
        ("c", 'Caricato'),
        ("a", 'Autorizzato'),
        ("n", 'Negato'),
        ("t", 'Terminato'),
        ("h", 'Chiuso'),
        ]
    status      = models.CharField(
                    max_length=1,
                    choices=STATUS_CHOICES,
                    default="m",
                )
    
    center      = models.ForeignKey(
                    Center,
                    on_delete=models.CASCADE,
                    blank=True,
                    null=True,
                )
    institution =  models.ForeignKey(
                    Institution,
                    on_delete=models.CASCADE,
                    blank=True,
                    null=True,
                )
    warning     = models.BooleanField(default=False, editable=False)
    def __str__(self):
        return "Prot. {num}".format(num=self.pk)

    def title(self):
        return self.course.feature.title
        
    def code(self):
        return self.course.code
        
    def getTrainers(self):
        return [x.trainer for x in self.session_set.all()]
        
    def getLearners(self):
        return [x.user for x in self.learners_set.all()]
    
    def checkHoursPracticeRequestMin(self):
        return self.getHoursPractice() - self.getHoursPracticeRequestMin()
        
    def getHoursPracticeRequestMin(self):
        h,m = time.timedelta_to_hm(getattr(self.course, self.type).practice)
        return h
            
    def getHoursTheoryRequest(self):
        h,m = time.timedelta_to_hm(getattr(self.course, self.type).theory)
        return h
    
    def getHoursTheory(self):
        ore_teoria_inserite = self.session_set.filter(subject_type="t").aggregate(
                    total_time=Sum(
                        ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())
                    )
                )['total_time']
        h,m = time.timedelta_to_hm(ore_teoria_inserite)
        return h
        
    def getDifferenceHoursTheory(self):
        # print("Protocol.getDifferenceHoursTheory", int(self.getHoursTheoryRequest())-int(self.getHoursTheory()))
        return int(self.getHoursTheoryRequest())-int(self.getHoursTheory())
        
    def checkHoursTheory(self):
        ore_teoria_inserite = self.getHoursTheory()
        ore_teoria = self.getHoursTheoryRequest()
        # print("checkHoursTheory", ore_teoria_inserite >= ore_teoria)
        return ore_teoria_inserite >= ore_teoria
        
    def getLearnersRequest(self):
        # return self.learners_set.count()
        return self.learners_request
        
    def checkNumTrainer(self):
        maxLearnersByTrainer = self.getPracticeLearnersPerTainer()
        if maxLearnersByTrainer <= 0: return True # nessun rapporto docenti/discenti
        trainers = self.session_set.filter(subject_type="p").count()
        learners = self.getLearnersRequest()
        
        min_trainer = int(math.ceil(learners/maxLearnersByTrainer))
        # print("Learners.checkNumTrainer", "pk:", self.id, 
                                          # "trainers:", trainers, 
                                          # "learners:", learners, 
                                          # "maxLearnersByTrainer:", maxLearnersByTrainer)
        # print("Learners.checkNumTrainer min_trainer", min_trainer, 
                                        # "Num trainer ok?", int(trainers) >= int(min_trainer) )
        return (int(trainers) >= int(min_trainer)) 

    def getMaxLearnersTheory(self):
        typeCourse = self.type
        return getattr(self.course, typeCourse).max_learners_theory

    def getMaxLearnersPractice(self):
        return self.getPracticeLearnersPerTainer()

    def getPracticeLearnersPerTainer(self):
        typeCourse = self.type
        return getattr(self.course, typeCourse).max_learners_practice

    def getAuthorizationMessage(self):
        if self.course.need_institution:
            return  _("Training project authorized by the trainer {0} with protocol {1} ​​of {2}.".format(self.institution, "xxx", "YYY"))
        return  _("Activities planned by the employer and provided through a qualified person pursuant to the D.M. March 6, 2013.")
    
    def getRequalifictionMessage(self):
        return  _("Qualification update within {0} years.".format(self.course.feature.years))
    
    def getQualification(self):
        return self.session_set.latest('date').date
        
    def getExpiration(self):
        years = self.course.feature.years
        qual  = self.getQualification() #session_set.latest('date').date
        return qual.replace(year = qual.year + years)

    def expired(self):
        print(type(self.getExpiration()))
        now = datetime.date.today()
        return self.getExpiration() < now

    def checkPractice(self):
        h = self.getHoursPracticeRequestMin()
        return h>0
        
    def checkHoursPractice(self):
        if not self.checkNumTrainer(): return False
        hoursInsertPractice = self.getHoursPractice()
        h = self.getHoursPracticeRequest()
        # print("Protocol.checkHoursPractice", h, "learners:",self.learners_set.count(), "Ore/doc", self.getPracticeLearnersPerTainer())
        return (hoursInsertPractice >= h)
    
    def getDifferenceHoursPractice(self):
        return int(self.getHoursPractice()) - int(self.getHoursPracticeRequest())
        
    def getHoursPracticeRequest(self):
        learners = self.getLearnersRequest()
        hoursPractice,m = time.timedelta_to_hm(getattr(self.course, self.type).practice)
        if self.getPracticeLearnersPerTainer() <= 0: return 0 # nessun discente previsto
        h = hoursPractice * math.ceil(learners / self.getPracticeLearnersPerTainer() )
        return h
        
    def getHoursPractice(self):
        hours = self.session_set.filter(subject_type="p").aggregate(
                    total_time=Sum(
                        ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField()),
                    )
                )['total_time']
        h,m = time.timedelta_to_hm(hours)
        # print("Protocol.getHoursPractice", h, hours)
        return h
    
    def checkAll(self):
        # print("Protocol.checkAll",self.checkHoursTheory , self.checkHoursPractice , self.checkNumTrainer)
        return self.checkHoursTheory() and self.checkHoursPractice() and self.checkNumTrainer()
    
    def checkAllSignedFiles(self):
        # print(self.files_set.all())
        # print([x.signs_set.all().count()>0 for x in self.files_set.all()])
        if False in [x.signs_set.all().count()>0 for x in self.files_set.all()]:
            # print("False")
            return False
        return True
        
    def checkAllCertificateLoads(self):
        # print("checkAllCertificateLoads", [x.inst_cert.name!="" for x in self.learners_set.filter(passed=True)])
        if False in [x.inst_cert.name!="" for x in self.learners_set.filter(passed=True)]:
            return False
        return True

    def status_close(self):
        return self.status == "h"

class Session(models.Model):
    protocol    = models.ForeignKey(
                    Protocol,
                    on_delete=models.CASCADE,
                )
    trainer     = models.ForeignKey(
                    User,
                    on_delete=models.CASCADE,
                    null=True, 
                    # blank=True
                )
    country     = models.ForeignKey(
                    Country,
                    on_delete=models.CASCADE,
                    null=True, 
                    # blank=True
                )
    city        = models.ForeignKey(
                    City,
                    on_delete=models.CASCADE,
                    null=True, 
                    # blank=True
                )
    address     = models.CharField(max_length=255, default="",null=True)
    TYPE_CHOICES = [
        ("t", _('Theory')),
        ("p", _('Practice')),
        ]
    subject_type    = models.CharField(
                    max_length=25,
                    choices=TYPE_CHOICES,
                    default="t",
                )
    EXECUTION_CHOICES = [
        ("front", _('In presence')),
        ("online", _('On the web')),
        ]
    execution   =  models.CharField(
                    max_length=25,
                    choices=EXECUTION_CHOICES,
                    default="front",
                )
    date        = models.DateField(null=True)
    start_time  = models.TimeField(null=True)
    end_time    = models.TimeField(null=True)
    
    # @property
    # def type(self):
        # return self.subject_type
        
    def __str__(self):
        return _("Session {data} {inizio}/{fine}".format(data=self.date, 
                                            inizio=self.start_time, 
                                            fine=self.end_time
                                        ))
    
    def getPlace(self):
        return "{0} {1}".format(self.city, self.address)
        
    def getTheoryTimes(self, date, start_time, end_time):
        "Sovrapposizione di orari nella stessa data per la teoria"
        # return
        return Session.objects.filter(
                                (Q(start_time__lt=start_time) & Q(end_time__gt=start_time))
                                |
                                (Q(start_time__lt=end_time) & Q(end_time__gt=end_time))
                                |
                                (Q(start_time__gt=start_time) & Q(start_time__lt=end_time))
                                |
                                (Q(end_time__gt=start_time) & Q(end_time__lt=end_time)),
                                subject_type="t", date=date, pk=self.pk,
                                )  #.exclude()
                                
    def getDateTimeRange(self, trainer, date, start_time, end_time):
        "Impegni del Trainer diviso per data ed orario"
        return Session.objects.filter( trainer=trainer,
                                date=date, 
                                start_time__lte=start_time, 
                                end_time__gte=end_time).exclude(pk=self.pk)
    
    def isSignedInProtocol(self):
        learners = self.protocol.learners_set.all()
        for learner in learners:
            if learner.user == self.trainer:
                return self.trainer
        return False
        
    def isBusyInstance(self):
        return self.isBusy(self.trainer)
    
    def isBusy(self, learner):
        sessions = self.protocol.session_set.all()
        for session in sessions:
            date = session.date
            start_time = session.start_time
            end_time = session.end_time
            if Protocol.objects.filter( learners__user=learner,
                                session__date=date, 
                                session__start_time__lte=start_time, 
                                session__end_time__gte=end_time
                                ).exclude(pk=self.protocol.pk):
                return True
        return False
        
def file_path_name_learner(instance, file_name):
    file_root, file_ext = os.path.splitext(file_name)
    return "prot_{0}_{1}_{2}".format(instance.protocol.id, "cert_inst", file_ext)
class Learners(models.Model):
    protocol    = models.ForeignKey(
                    Protocol,
                    on_delete=models.CASCADE,
                )
    user        = models.ForeignKey(
                User,
                on_delete=models.CASCADE,
                null=True, blank=True
            )
    passed      = models.BooleanField(default=False)
    inst_cert   = models.FileField(upload_to=file_path_name_learner, 
                                   storage=FileInstCertStorage(location='files/', base_url="/document"),
                                   blank=True,
                                   validators=[validate_file_size, validate_file_extension],
                                   verbose_name=_("Certificate Institution")
                                  )
                                  
    class Meta:
        ordering = ['user__last_name']
        unique_together = ('protocol', 'user',)
        
    def __str__(self):
        return _("User: {nome} {cognome} ({user}) ".format(user=self.user.username, 
                                            nome=self.user.first_name, 
                                            cognome=self.user.last_name
                                        ))
     
    def isSignedInProtocol(self):
        sessions = self.protocol.session_set.all()
        for session in sessions:
            if self.user == session.trainer:
                return self.user
        return False
        
    def isBusyInstance(self):
        return self.isBusy(self.user)
        
    def isBusy(self, learner):
        sessions = self.protocol.session_set.all()
        for session in sessions:
            date = session.date
            start_time = session.start_time
            end_time = session.end_time
            # print(date, start_time, end_time )
            if Protocol.objects.filter( learners__user=learner,
                                session__date=date, 
                                session__start_time__lte=start_time, 
                                session__end_time__gte=end_time
                                ).exclude(pk=self.protocol.pk):
                return True
        return False
    
    #todo: cancella il file se cancello il record
    # def delete(.....)

class Files(models.Model):
    protocol    = models.ForeignKey(
                    Protocol,
                    on_delete=models.CASCADE,
                )
    datetime    = models.DateTimeField(auto_now_add=True)
    owner       = models.ForeignKey(
                    User,
                    on_delete=models.CASCADE,
                    editable=False,
                    )
    TYPE_CHOICES = [
        ("r", _('Attendance register')),
        ("v", _('Exam reporter')),
        ("p", _('Privacy')),
        ("o", _('Other')),
        ]
    doc_type    = models.CharField(
                    max_length=2,
                    choices=TYPE_CHOICES,
                    default="r",
                    # required=True,
                )
    file        = models.FileField(upload_to=file_path_name, 
                                   storage=fs, blank=False,
                                   validators=[validate_file_size, validate_file_extension],
                                   # help_text="file help text"
                                  )
    class Meta:
        ordering = ['id']
        unique_together = ('protocol', 'doc_type',)
    
    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)
        
    def __str__(self):
        # print("Files.__str__", type(self.file))
        return "Files"+self.get_doc_type_display()

    def check_signed(self):
        if self.signs_set.all():
            return True
        return False
        
    def check_file(self):
        # print(self.file.storage.url(self.file.name))
        # print(dir(self.file.storage))
        if self.file.name:
            return True 
        else:
            return False
    
    def getSignedFile(self):
        return self.file.storage.getSignedFileName(self.file.name)
        
    def get_signed_or_master(self):
        if self.file.storage.getSignedFileName(self.file.name):
            return self.file.storage.getSignedFileName(self.file.name)
        else:
            return self.file.name
        
    def signFile(self, u=None, data=None):
        # print("Files.signFile")
        # print(self.file.name)
        # Genera il file se esiste almeno una firma associata
        if self.signs_set.all():
            self.file.storage.signFile(self.file.name, self)
        else:
            #altrimenti cancella il file "xxxx_signed.pdf" se esiste
            if self.file.storage.checkSigned(self.file.name):
                self.file.storage.delete(self.file.storage.checkSigned(self.file.name))
        
    def _openSignFile(self):
        from django.utils.safestring import SafeString
        from django.urls import reverse_lazy

        html = "<a class='digi-btn digi-bg-primary' href='{0}'>{1}</a>".format(
                    reverse_lazy("admin:sign-file", kwargs={'pk':self.protocol.id, 'file_id':self.id}),
                    _("Sign"))
        return SafeString(html)
    
    def html(self):
        return self._openSignFile()

        
# Authorizations by Institutions        
class Authorizations(models.Model):
    protocol    = models.ForeignKey(
                    Protocol,
                    on_delete=models.CASCADE,
                )
    datetime    = models.DateTimeField(auto_now_add=True)
    owner       = models.ForeignKey(
                    User,
                    on_delete=models.CASCADE,
                    editable=False,
                    )
    TYPE_CHOICES = [
        ("a", _('Authorization')),
        # ("o", _('Other informations')),
        ]
    doc_type    = models.CharField(
                    max_length=2,
                    choices=TYPE_CHOICES,
                    default="a",
                    # required=True,
                )
    auth_prot   = models.CharField(max_length=20, default="")
    file        = models.FileField(upload_to=file_path_name, 
                                   storage=fs, blank=False,
                                   validators=[validate_file_size, validate_file_extension],
                                  )
    class Meta:
        ordering = ['id']
        unique_together = ('protocol', 'doc_type',)
    
    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)
        
    def __str__(self):
        # print("Files.__str__", type(self.file))
        return "Authorizations"


class Action(models.Model):
    protocol    = models.ForeignKey(
                    Protocol,
                    on_delete=models.CASCADE,
                )
    owner       = models.ForeignKey(
                    User,
                    on_delete=models.CASCADE,
                    editable=False,
                    )
    datetime    = models.DateTimeField(auto_now_add=True)
    text        = models.CharField(max_length=255, default="")
    info        = models.TextField(default="")


import uuid
class Signs(models.Model):
    uiid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    file = models.ForeignKey(
                    Files,
                    on_delete=models.CASCADE,
                )
    user = models.ForeignKey(
                    User,
                    on_delete=models.CASCADE,
                    editable=False,
                )
    
    pdf_x     =  models.IntegerField(default=0)
    pdf_y     =  models.IntegerField(default=0)
    html_x    =  models.IntegerField(default=0)
    html_y    =  models.IntegerField(default=0)
    page      =  models.IntegerField(default=0)
    