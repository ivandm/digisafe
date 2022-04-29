"""Markers serializers."""
from rest_framework_gis import serializers as gisserializers
from rest_framework import serializers
from django.core import serializers as djangoserializers

import datetime

from agenda.models import Agenda, AgendaFeatures
from job.models import Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'title', 'code', 'description']


class DefaultPositionSerializer(gisserializers.GeoFeatureModelSerializer):
    """Markers Agenda GeoJSON serializer."""

    class Meta:
        """Markers Marker serializer meta class."""
        fields = ("id",)
        geo_field = "default_position"
        model = AgendaFeatures

    def get_properties(self, instance, fields):
        # print("maps.serializers.DefaultPositionSerializer")
        # print(instance, fields)
        properties = super(DefaultPositionSerializer, self).get_properties(instance, fields)
        request = self.context['request']
        exclude = ""
        date_in = request.GET.get("date_in", "")
        date_out = request.GET.get("date_out", "")
        if date_in != "" and date_out != "":
            date_in_obj = datetime.datetime.strptime(date_in, '%Y-%m-%d').date()
            date_out_obj = datetime.datetime.strptime(date_out, '%Y-%m-%d').date()
            items = instance.user.agenda_set.filter(
                        date_start__date__gte=date_in_obj,
                        date_end__date__lte=date_out_obj
            )
            # print("items", items)
            agenda = djangoserializers.serialize("json", items)
            # print(agenda)
            for i in items:
                if i.busy:
                    exclude += "<br><span class='text-danger'>{}/{} <i>Busy</i> {}</span>".format(i.date_start.date(), i.date_end.date(), i.city_name)
                else:
                    exclude += "<br><span class='text-success'>{}/{} <i>Free</i> {}</span>".format(i.date_start.date(), i.date_end.date(), i.city_name)

        if exclude:
            exclude = "Outsite dates:" + exclude
        marker_info = "<b>{}</b> <br> {}".format(instance.user, exclude)
        properties["marker_info"] = marker_info
        properties["agenda"] = agenda
        properties["user"] = "{}".format(instance.user.getFullName)
        properties["user_id"] = "{}".format(instance.user.id)
        properties["date_range_start"] = "{}".format(instance.user.last_name)
        properties["date_range_end"] = "{}".format(instance.user.last_name)
        properties["tooltip"] = "{} {}".format(instance.user.last_name, instance.user.first_name)
        return properties


class AgendaFreeSerializer(gisserializers.GeoFeatureModelSerializer):
    """Markers Agenda GeoJSON serializer."""

    class Meta:
        """Markers Marker serializer meta class."""

        fields = ("id",)
        geo_field = "city"
        model = Agenda

    def get_properties(self, instance, fields):
        # print("maps.serializers.AgendaSerializer")
        # print(instance, fields)
        properties = super(AgendaFreeSerializer, self).get_properties(instance, fields)
        marker_info = "<b>{}</b><br><i>{}</i></b><br> <b>Free date:</b><br>From {} to {}".format(
                                                                    instance.user,
                                                                    instance.object,
                                                                    instance.date_start.date(),
                                                                    instance.date_end.date())
        properties["marker_info"] = marker_info
        properties["user"] = "{}".format(instance.user.getFullName)
        properties["user_id"] = "{}".format(instance.user.id)
        properties["busy_free"] = "Free"
        properties["busy"] = instance.busy
        properties["tooltip"] = "{} {}".format(instance.user.last_name, instance.user.first_name)
        properties["date_start"] = "{}".format(instance.date_start.date())
        properties["date_end"] = "{}".format(instance.date_end.date())
        return properties


class AgendaBusySerializer(gisserializers.GeoFeatureModelSerializer):
    """Markers Agenda GeoJSON serializer."""

    class Meta:
        """Markers Marker serializer meta class."""

        fields = ("id",)
        geo_field = "city"
        model = Agenda

    def get_properties(self, instance, fields):
        # print("maps.serializers.AgendaSerializer")
        # print(instance, fields)
        properties = super(AgendaBusySerializer, self).get_properties(instance, fields)
        marker_info = "<b>{}</b><br><i>{}</i></b><br> <b>Busy date:</b><br>From {} to {}".format(
                                                                    instance.user,
                                                                    instance.object,
                                                                    instance.date_start.date(),
                                                                    instance.date_end.date())
        properties["marker_info"] = marker_info
        properties["user"] = "{}".format(instance.user.getFullName)
        properties["user_id"] = "{}".format(instance.user.id)
        properties["busy_free"] = "Busy"
        properties["busy"] = instance.busy
        properties["tooltip"] = "{} {}".format(instance.user.last_name, instance.user.first_name)
        properties["date_start"] = "{}".format(instance.date_start.date())
        properties["date_end"] = "{}".format(instance.date_end.date())
        return properties

