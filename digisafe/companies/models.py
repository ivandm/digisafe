from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db.models import Sum, Count
import os
import uuid

from digisafe import storage
from users.models import User
from countries.models import Country, City
from job.models import Job


class Company(models.Model):
    name = models.CharField(max_length=255)
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


# * Booking Models START * #


class SessionBook(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    note = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    expire_date = models.DateTimeField()
    jobs = models.ManyToManyField(Job)
    user_option_list = models.ManyToManyField(User, blank=True)
    user_decline_list = models.ManyToManyField(User, related_name="sessionbook_user_decline", blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return "{}".format(self.name)

    def user_option_list_secure_remove(self, user):
        """
        Rimuove user dalla lista in modo sicuro.
        Rimuove solo se non presente nella lista 'user' e 'users_confirm' di DateBook.
        """
        # print("companies.models.SessionBook.user_option_list_secure_remove")
        if not self.datebook_set.filter(users_confirm=user) \
                and not self.datebook_set.filter(users=user) \
                and not self.user_decline_list.filter(pk=user.id):
            # print("No booked and confirm and declined", "Rimuovi")
            self.user_option_list.remove(user)
            return True
        # print("booked/confirmed/declined. non rimosso")
        return "User have been booked or confirmed"

    def range_date(self):
        return "{}/{}".format(self.start_date, self.end_date)

    def send_book_invite(self):
        print("companies.models.SessionBook.send_book_invite")
        date_list = [x.date.strftime("%d-%m-%Y") for x in self.datebook_set.all()]
        dates = "\n".join(date_list)
        for u in self.user_option_list.all():

            subject = "Invite book session from {}. Open until date {}".format(self.company, self.expire_date.date())
            msg =""" 
Dear {username},

You have been invited to book on work session id {session_id}

Session name: {session_name}
Address: {address}
Expiration date: {exp_date}

Work session dates:
{dates}

Link to choose the date
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
                exp_date=self.expire_date.date(),
                dates=dates,
            )
            u.sendSystemEmail(subject, msg)

    def total_users_request(self):
        return self.datebook_set.aggregate(Sum("number_user"))["number_user__sum"]

    def total_users_booked(self):
        return self.datebook_set.aggregate(Count("users"))["users__count"]

    def total_users_confirmed(self):
        return self.datebook_set.aggregate(Count("users_confirm"))["users_confirm__count"]

    def is_full(self):
        for db in self.datebook_set.all():
            if db.number_user != db.users_confirm.count():
                return False
        return True

    def booked_users(self):
        # print("companies.models.SessionBook.booked_users")
        datas = self.datebook_set.all().values_list('users', flat=True).order_by('users').distinct()
        return datas

    def booked_dates(self):
        # print("companies.models.SessionBook.booked_dates")
        datas = self.datebook_set.all().values_list('users', 'date').order_by('users')
        return datas

    def confirmed_users(self):
        # print("companies.models.SessionBook.booked_confirmed")
        datas = self.datebook_set.all().values_list('users_confirm', flat=True).order_by('users_confirm').distinct()
        return datas


class DateBook(models.Model):
    session = models.ForeignKey(SessionBook, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="job_datebook")
    number_user = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    date = models.DateField()
    users = models.ManyToManyField(User, blank=True)  # Utenti prenotati
    users_confirm = models.ManyToManyField(User,
                                           blank=True,
                                           related_name="datebook_confirm")  # Utenti accettati dalla company

    def __str__(self):
        return "{} {} {}".format(self.session.name, self.date, self.job)

    def users_display(self):
        return [x.getFullName for x in self.users.all()]

    def confirm_display(self):
        return [x.getFullName for x in self.users_confirm.all()]

    def user_booked(self):
        res = self.users.all().exclude(id__in=self.users_confirm.all())
        return res

    def is_full(self):
        return self.number_user == self.users_confirm.count()

# * END Booking Models * #
