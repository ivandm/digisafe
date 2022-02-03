from django.db import models
from users.models import User


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
        
class Profile(models.Model):
    company = models.OneToOneField(
                        Company,
                        on_delete=models.CASCADE,
                    )
    address = models.CharField(max_length=255)
    
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
    