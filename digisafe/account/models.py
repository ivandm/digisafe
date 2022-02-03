from django.db import models
from django.conf import settings
from django.utils.translation import ngettext, gettext as _
import uuid
from djgeojson.fields import PointField

class UsersPosition(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    geom      = PointField()
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.user)

    @property
    def popupContent(self):
        return '<p>{0} {1}</p><p>{2}: {3}</p><p><a id="useragenda" href="">Agenda</a></p>'.format(
            self.user.last_name,
            self.user.first_name,
            _("Last update"),
            self.timestamp.strftime("%d/%m/%Y"),
        )

    def setGeom(self, lat, lon):
        self.geom = {'type': 'Point', 'coordinates': [float(lat), float(lon)]}

class TmpPassword(models.Model):
    user = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    )
    timestamp = models.DateTimeField(auto_now_add=True)
    cod_auth  = models.UUIDField(default=uuid.uuid4)
    ip        = models.GenericIPAddressField()
    
    def set_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        self.ip = ip
        
        