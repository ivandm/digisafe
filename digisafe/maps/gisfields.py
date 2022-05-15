from django.contrib.gis.db import models as gismodel
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from functools import partialmethod
from functools import partial
from geopy.geocoders import Nominatim


def _get_city_name(self, field):
    # print("maps.gisFields.PointField.getCityName")
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


def _get_city_latlon(self, field):
    # print("maps.gisFields.PointField._get_city_latlon")
    return "Lat {:.2f}; Lon {:.2f}".format(self.city.y, self.city.x)


class PointField(gismodel.PointField):
    description = _("The base GIS field with digisafe custom methods.")

    def contribute_to_class(self, cls, name, **kwargs):
        # print("maps.gisFields.PointField.contribute_to_class")
        # print(cls, name)
        # print(kwargs)
        super().contribute_to_class(cls, name, **kwargs)
        setattr(
            cls, f'get_{name}_name',
            partialmethod(_get_city_name, field=self)
        )
        setattr(
            cls, f'get_{name}_latlon',
            partialmethod(_get_city_latlon, field=self)
        )

