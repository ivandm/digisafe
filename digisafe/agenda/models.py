from django.db import models
from django.contrib.gis.db import models as gismodel
from django.conf import settings
from django.utils.translation import gettext as _

from django.utils import translation
from functools import partial
from geopy.geocoders import Nominatim
from companies.models import DateBook

from maps import gisfields


class AgendaFeatures(gismodel.Model):
    user = gismodel.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    default_position = gismodel.PointField()

    def __str__(self):
        return "{} {} - Default position: {}".format(
            self.user.last_name, self.user.first_name, self.pos_name
        )

    @property
    def pos_name(self):
        # print("account.models.AgendaFeatures.pos_name")
        user_agent = "https://nominatim.openstreetmap.org/"
        geolocator = Nominatim(user_agent=user_agent)
        lang = translation.get_language()
        reverse = partial(geolocator.reverse, language="{}".format(lang))
        try:
            location = reverse("{lat}, {lon}".format(lat=self.default_position.y, lon=self.default_position.x))
            city = location.raw.get('address').get("city")
            country = location.raw.get('address').get("country")
            return "{} ({})".format(city, country)
        except:
            return ""


class Agenda(gismodel.Model):
    user = gismodel.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    timestamp = gismodel.DateTimeField(auto_now=True)
    # city = gismodel.PointField()
    city = gisfields.PointField()
    busy = models.BooleanField(default=True)
    date_start = gismodel.DateTimeField()
    date_end = gismodel.DateTimeField()
    object = gismodel.CharField(max_length=100, default="", blank=False)
    description = gismodel.TextField(max_length=500, default="", blank=True)
    datebook = models.ForeignKey(DateBook, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return "Agenda Events: {} {}/{}".format(self.object, self.date_start.date(), self.date_end.date())

    def jobs(self):
        return [x.title for x in self.user.jobprofile.job.all()]

    def date_start_date(self):
        # print("account.models.Agenda.date_start_date", self.date_start.date())
        return self.date_start.date()

    def date_end_date(self):
        return self.date_end.date()

    def marker_info(self):
        return _("<b>{}</b> <br><b>{}</b> <br>Busy from {} to {}".format(self.user.first_name, self.object, self.date_start.strftime("%d-%m-%Y"), self.date_end.strftime("%d-%m-%Y")))

    def date_range(self):
        return "{}/{}".format(self.date_start.date(), self.date_end.date())

    @property
    def city_name(self):
        # print("account.models.Agenda.city_name")
        user_agent = "https://nominatim.openstreetmap.org/"
        geolocator = Nominatim(user_agent=user_agent)
        lang = translation.get_language()
        reverse = partial(geolocator.reverse, language="{}".format(lang))
        try:
            location = reverse("{lat}, {lon}".format(lat=self.city.y, lon=self.city.x))
            city = location.raw.get('address').get("city")
            country = location.raw.get('address').get("country")
            return "{} ({})".format(city, country)
        except:
            return ""
