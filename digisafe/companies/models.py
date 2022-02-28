from django.db import models
import os

from digisafe import storage
from users.models import User
from countries.models import Country, City

class Company(models.Model):
    name   = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    admins = models.ManyToManyField(
                User,
                blank=True,
                related_name = "admins_company"
            )
    associates = models.ManyToManyField(
                User,
                blank=True,
                related_name = "associates_company"
            )

    def __str__(self):
        return "{0}".format(self.name)

    def list_admins(self):
        from django.utils.safestring import mark_safe
        res = ["{0} {1}<br>".format(x.last_name.upper() , x.first_name.upper() ) for x in self.admins.all()]
        html = "".join(res)
        return mark_safe(html)

def file_path_name_company(instance, file_name):
    prefix = "logo_company"
    file_root, file_ext = os.path.splitext(file_name)
    return "{}_{}_{}".format(prefix, instance.id, file_ext)

class Profile(models.Model):
    company = models.OneToOneField(
                        Company,
                        on_delete=models.CASCADE,
                    )
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        null=True,
        # blank=True
    )
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        null=True,
        # blank=True
    )
    address = models.CharField(max_length=255)
    desc = models.TextField(default="")
    logo = models.FileField(
                    upload_to=file_path_name_company,
                    storage=storage.FileSystemStorage(location='static/imgs/', base_url="/imgs"),
                    validators=[storage.validate_file_size, storage.validate_file_extension_img],
                  )

    def __str__(self):
        return "{}".format(self.company.name)
    
class requestAssociatePending(models.Model):
    user = models.ForeignKey(
                User,
                on_delete=models.CASCADE,
                blank=True,
            )
    company = models.ForeignKey(
                Company,
                on_delete=models.CASCADE,
                blank=True,
            )
    user_req    = models.BooleanField(default=False)
    company_req = models.BooleanField(default=False)
    