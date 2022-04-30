from django.db import models
from django.conf import settings
from django.utils.translation import ngettext, gettext as _
import uuid


class TmpPassword(models.Model):
    user = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    )
    timestamp = models.DateTimeField(auto_now_add=True)
    cod_auth = models.UUIDField(default=uuid.uuid4)
    ip = models.GenericIPAddressField()
    
    def set_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        self.ip = ip
        
        