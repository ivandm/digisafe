from django.db import models
from django.urls import reverse
from django.conf import settings
import os, uuid

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

    favorite = models.ManyToManyField(
                User,
                blank=True,
                related_name = "favorite_company"
            )

    def __str__(self):
        return "{0}".format(self.name)

    def list_admins(self):
        from django.utils.safestring import mark_safe
        res = ["{0} {1}<br>".format(x.last_name.upper() , x.first_name.upper() ) for x in self.admins.all()]
        html = "".join(res)
        return mark_safe(html)

    def list_favorite(self):
        from django.utils.safestring import mark_safe
        res = ["{0} {1}<br>".format(x.last_name.upper() , x.first_name.upper() ) for x in self.favorite.all()]
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


# * Booking Models *


class SessionBook(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    note = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    expire_date = models.DateTimeField()
    user_option_list = models.ManyToManyField(User)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return "{}".format(self.name)

    def range_date(self):
        return "{}/{}".format(self.start_date, self.end_date)

    def send_book_invite(self):
        print("companies.models.SessionBook.send_book_invite")
        date_list = [x.date.strftime("%d-%m-%Y") for x in self.datebook_set.all()]
        dates = "\n".join(date_list)
        for u in self.user_option_list.all():

            subject = "Invite book session from {}".format(self.company)
            msg =""" 
Dear {username},

You have been invited to book on work session id {session_id}

Session name:
{session_name}

Address:
{address}

Work session dates:
{dates}

Link to choice dates
{url_choice_dates}?uuid={uuid}

            """.format(
                session_id=self.id,
                username=u.getFullName,
                url_choice_dates=settings.HTTP+settings.CURRENT_SITE+reverse(
                    "companies:sessionbook-bookresponse",
                    args=[self.id]
                ),
                uuid=self.uuid,
                session_name=self.name,
                address=self.address,
                dates=dates,
            )
            u.sendSystemEmail(subject, msg)


class DateBook(models.Model):
    session = models.ForeignKey(SessionBook, on_delete=models.CASCADE)
    date = models.DateField()
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return "{} {}".format(self.session.name, self.date)

    def users_display(self):
        return [x.last_name for x in self.users.all()]
