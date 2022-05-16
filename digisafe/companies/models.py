from django.db import models
from django.contrib.gis.db import models as gismodel
from django.urls import reverse
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db.models import Sum, Count
from django.utils import timezone
import os
import uuid

from maps import gisfields
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


class SessionBook(gismodel.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    # address = models.CharField(max_length=255)
    city = gisfields.PointField()
    # city = gismodel.PointField()
    note = models.TextField(blank=True)
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
        Rimuove user dalla lista 'user_option_list' in modo sicuro.
        Rimuove solo se non presente nella lista 'user' (prenotati) di DateBook (prenotato da parte dell'utente)
         e 'users_confirm' di DateBook (confermato prenotazione da parte della company).
        :param user: User object
        :return: bool True utente correttamente rimosso dalla lista
                 str con il motivo della mancata rimozione 'User have been booked or confirmed'
        """
        # print("companies.models.SessionBook.user_option_list_secure_remove")
        if not self.datebook_set.filter(users_confirm=user) \
                and not self.datebook_set.filter(users=user) \
                and not self.user_decline_list.filter(id=user.id):
            # print("No booked and confirm and declined", "Rimuovi")
            self.user_option_list.remove(user)
            return True
        # print("booked/confirmed/declined. non rimosso")
        return "User have been booked or confirmed. Can't remove."

    def user_option_list_add(self, user):
        """
        Aggiunge un utente alla lista invitati user_option_list, se:
        - non è nella lista declinati user_decline_list
        :param user: object User
        :return: bool True if add in list
                 str message "User have been declined"
        """
        # print("companies.models.SessionBook.user_option_list_add")
        if self.declined_user(user.id):
            return "User have been declined"
        self.user_option_list.add(user)
        return True

    def user_decline_list_add(self, user):
        """
        Utente declina l'invito, se:
        - Company non ha già confermato una prenotazione
        :param user: User object
        :return: bool True: utente ha declinato, False utente non ha declinato
        """
        # print("companies.models.SessionBook.user_decline_list_add")
        if self.datebook_set.filter(session=self.id).exclude(users_confirm=user):
            self.user_decline_list.add(user)
            # Viene cancellato dalle ventuali prenotazioni
            for db in self.datebook_set.all():
                db.users.remove(user)
                db.users_confirm.remove(user)
            # Cancellare tutte le date in agenda (siccome declina anche con date prenotate)
            user.agenda_remove_sessionbook(self)

            # todo: notifica alla company l'azione di declino
            return True
        return False

    def range_date(self):
        """
        Range delle date della work session
        :return: str
        """
        return "{}/{}".format(self.start_date, self.end_date)

    def send_book_invite(self):
        """
        Invia una email di invito agli utenti nella lista invitati.
        Usa il metodo 'sendSystemEmail' di User.
        :return: None
        """
        # print("companies.models.SessionBook.send_book_invite")
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
        """
        Numero totale di utenti richiesti nella work session.
        Somma le giornate con il numero di operatori richiesti per ogni giornata
        :return: int
        """
        return self.datebook_set.aggregate(Sum("number_user"))["number_user__sum"]

    def total_users_booked(self):
        """
        Numero totale di utenti prenotati
        :return: int
        """
        return self.datebook_set.aggregate(Count("users"))["users__count"]

    def total_users_confirmed(self):
        """
        Numero totale di utenti confermati
        :return: int
        """
        return self.datebook_set.aggregate(Count("users_confirm"))["users_confirm__count"]

    def is_expired(self):
        """
        Controlla se ha superato la data di scadenza per le prenotazioni
        :return: bool
        """
        return timezone.now() > self.expire_date

    def is_full(self):
        """
        Verifica se una work session è al completo
        :return: bool
        """
        for db in self.datebook_set.all():
            if db.number_user != db.users_confirm.count():
                return False
        return True

    def declined_user(self, user_id):
        """
        Cerca un utente nella lista dei declinati
        :param user_id:
        :return: QuerySet object
        """
        return self.user_decline_list.filter(pk=user_id)

    def declined_users(self):
        """
        Lista utenti che hanno declinato
        :return: QuerySet object
        """
        return self.user_decline_list.all()

    def invited_user(self, user_id):
        """
        Cerca un utente nella lista invitati 'user_option_list'
        :param user_id: pk object User
        :return: QuerySet list object
        """
        return self.user_option_list.filter(pk=user_id)

    def invited_users(self):
        """
        Lista utenti invitati
        :return: QuerySet list object
        """
        return self.user_option_list.all()

    def booked_users(self):
        """
        Lista utenti che hanno prenotato almeno una data in DateBook
        :return: QuerySet list object
        """
        # print("companies.models.SessionBook.booked_users")
        datas = self.datebook_set.all().values_list('users', flat=True).order_by('users').distinct()
        return datas

    def booked_dates(self):
        """
        Lista degli utenti con le date prenotate.
        :return: QuerySet list object
        """
        # print("companies.models.SessionBook.booked_dates")
        datas = self.datebook_set.all().values_list('users', 'date').order_by('users')
        return datas

    def confirmed_dates(self):
        """
        Lista degli utenti con le date confermate.
        :return: QuerySet list object
        """
        # print("companies.models.SessionBook.booked_dates")
        datas = self.datebook_set.all().values_list('users_confirm', 'date').order_by('users')
        return datas

    def confirmed_users(self):
        """
        Lista utenti con le prenotazioni confermate
        :return: QuerySet flat list object <QuerySet [None, id]>
        """
        print("companies.models.SessionBook.booked_confirmed")
        datas = self.datebook_set.all().values_list('users_confirm', flat=True).order_by('users_confirm').distinct()
        print(datas)
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
    user_note = models.CharField(max_length=255, blank=True, null=True)
    company_note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return "{} {} {}".format(self.session.name, self.date, self.job)

    def user_book_add(self, user):
        """
        Aggiunge un utente alla lista prenotati, se:
        - la DateBook non è al completo, AND
        - la sessione non è scaduta
        :param user: User object
        :return: bool True se aggiunto
                 str 'Date is full, or booking session date is expired.'
        """
        if self.is_full() and self.session.expire_date <= timezone.now():
            return "Date is full, or booking session date is expired."
        self.users.add(user)
        return True

    def user_book_remove(self, user):
        """
        Rimuove un utente dalla lista prenotati, se:
        - utente non presente nella lista confermati
        :param user: User object
        :return: bool True se rimosso
                 str 'User is confirmed' non rimosso
        """
        if self.confirmed_user(user.id):
            return "User is confirmed. Can't remove it from booked list"
        self.users.remove(user)
        return True

    def confirm_user_add(self, user):
        """
        Aggiunge un utente alla lista dei confermati, se:
        - presente nella lista dei prenotati AND
        - NON presente nella lista dei confermati (Serve?)
        :param user: User Object
        :return: bool True se aggiunto
                 str 'User not booked or yet confirmed. Can't add in confirmed list'
        """
        if self.booked_user_not_confirmed(user.id):
            self.users_confirm.add(user)
            return True
        return "User not booked or yet confirmed. Can't add in confirmed list"

    def confirm_user_remove(self, user):
        """
        Rimuove un utente dalla lista dei confermati, se:
        - la data di scadenza delle modifiche alla work session non è superata
        :param user: User object
        :return: bool True se rimosso
                 str 'Expiration modify date passed. Can't remove.'
        """
        if self.session.expire_date <= timezone.now():
            self.users_confirm.remove(user)
            return True
        return "Expiration modify date passed. Can't remove."

    def confirmed_user(self, user_id):
        """
        Controlla se un utente è stato confermato
        :param user_id: 
        :return: QuerySet object
        """
        return self.users_confirm.filter(pk=user_id)

    def users_display(self):
        """
        (depreacto)
        Lista dei nomi degli utenti prenotati
        :return: list of str
        """
        return [x.getFullName for x in self.users.all()]

    def getName_booked_display_list(self):
        """
        Lista dei nomi degli utenti prenotati
        :return: list of str
        """
        return [x.getFullName for x in self.users.all()]

    def confirm_display(self):
        """
        (depreacto)
        Lista dei nomi degli utenti confermati
        :return: list of str
        """
        return [x.getFullName for x in self.users_confirm.all()]

    def getName_confirmed_display_list(self):
        """
        Lista dei nomi degli utenti confermati
        :return: list of str
        """
        return [x.getFullName for x in self.users_confirm.all()]

    def user_booked(self):
        """
        (Deprecato)
        Lista degli utenti che hanno prenotano e non ancora confermati
        :return: QuerySet object
        """
        res = self.users.all().exclude(id__in=self.users_confirm.all())
        return res

    def booked_user_not_confirmed(self, user_id):
        """
        Controlla se un utente è presente nella lista dei confermati
        :return: QuerySet object
        """
        res = self.users.filter(pk=user_id).exclude(id__in=self.users_confirm.all())
        return res

    def booked_users_not_confirmed(self):
        """
        Lista degli utenti che hanno prenotano e non ancora confermati
        :return: QuerySet object
        """
        res = self.users.all().exclude(id__in=self.users_confirm.all())
        return res

    def is_full(self):
        """
        Controlla se la data è al completo
        :return: bool
        """
        # print("companies.models.DateBook.is_full")
        return self.users_confirm.all().count() >= self.number_user

# * END Booking Models * #
