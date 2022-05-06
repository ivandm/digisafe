"""Markers API views."""
from rest_framework import viewsets
from rest_framework_gis import filters
from rest_framework import permissions
from django.db.models import Q
from django.contrib.gis.geos import Polygon

import datetime
from itertools import chain

from job.models import Job
from users.models import User, JobProfile
from agenda.models import Agenda, AgendaFeatures
from .serializers import DefaultPositionSerializer, JobSerializer, AgendaFreeSerializer, AgendaBusySerializer


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    """List filtered Jobs in view set."""

    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # print("maps.viewset.JobViewSet.get_queryset", self.request.GET)
        qs = self.request.GET.get("qs", "")

        return Job.objects.filter(title__icontains=qs)


class DefaultPositionViewSet(viewsets.ReadOnlyModelViewSet):
    """Marker Agenda default position view set."""

    bbox_filter_field = "default_position"
    filter_backends = (filters.InBBoxFilter,)
    queryset = AgendaFeatures.objects.all()
    serializer_class = DefaultPositionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # print("maps.viewset.JobViewSet")
        # print("filter_queryset self.request.GET", self.request.GET)
        date_in = self.request.GET.get("date_in", "")
        date_out = self.request.GET.get("date_out", "")
        if date_in == "" or date_out == "":
            return AgendaFeatures.objects.none()
        company_id = self.request.session["company_id"]
        # print("company_id", company_id)
        qs = self.request.GET.get("search", "")
        favorite = self.request.GET.get("favorite", False)
        # print("favorite", favorite)
        queryset = AgendaFeatures.objects.filter(user__jobprofile__job__title=qs)
        # print(queryset)
        if favorite == 'true':
            queryset = queryset.filter(user__favorite_company__id=company_id)
        elif favorite == 'false':
            queryset = queryset.exclude(user__favorite_company__id=company_id)
        # print("queryset", queryset)
        return queryset


class DefaultPositionViewSet2(viewsets.ReadOnlyModelViewSet):
    """Marker Agenda default position view set."""

    bbox_filter_field = "default_position"
    filter_backends = (filters.InBBoxFilter,)
    queryset = AgendaFeatures.objects.all()
    serializer_class = DefaultPositionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # print("maps.viewset.JobViewSet")
        # print("filter_queryset self.request.GET", self.request.GET)
        date_in = self.request.GET.get("date_in", "")
        date_out = self.request.GET.get("date_out", "")
        if date_in == "" or date_out == "":
            return AgendaFeatures.objects.none()
        company_id = self.request.session["company_id"]
        # print("company_id", company_id)
        favorite = self.request.GET.get("favorite", False)
        # print("favorite", favorite)

        qs = self.request.GET.getlist("search", "")
        bbox = self.request.GET.get("in_bbox", "").split(",")
        geom = Polygon.from_bbox(bbox)
        queryset = AgendaFeatures.objects.filter(
            user__jobprofile__job__title__in=qs,
            default_position__within=geom,
        ).distinct()

        if favorite == 'true':
            queryset = queryset.filter(user__favorite_company__id=company_id)
        elif favorite == 'false':
            queryset = queryset.exclude(user__favorite_company__id=company_id)
        # print("queryset", queryset)
        return queryset


class AgendaFreeViewSet(viewsets.ReadOnlyModelViewSet):
    """Marker JAgenda view set."""

    bbox_filter_field = "city"
    filter_backends = (filters.InBBoxFilter,)
    queryset = Agenda.objects.all()
    serializer_class = AgendaFreeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # print("maps.viewset.AgendaFreeViewSet")
        # print("filter_queryset self.request.GET", self.request.GET)
        date_in = self.request.GET.get("date_in", "")
        date_out = self.request.GET.get("date_out", "")
        if date_in == "" or date_out == "":
            return Agenda.objects.none()
        company_id = self.request.session["company_id"]
        qs = self.request.GET.get("search", "")
        favorite = self.request.GET.get("favorite", False)
        queryset = Agenda.objects.filter(user__jobprofile__job__title=qs, busy=False)
        if date_in and date_out:
            date_in_obj = datetime.datetime.strptime(date_in, '%Y-%m-%d').date()
            date_out_obj = datetime.datetime.strptime(date_out, '%Y-%m-%d').date()
            queryset = queryset.filter(
                date_start__date__gte=date_in_obj,
                date_end__date__lte=date_out_obj,
            )
        if favorite == 'true':
            queryset = queryset.filter(user__favorite_company__id=company_id)
        elif favorite == 'false':
            queryset = queryset.exclude(user__favorite_company__id=company_id)
        # print("queryset", queryset)
        return queryset


class AgendaFreeViewSet2(viewsets.ReadOnlyModelViewSet):
    """Marker JAgenda view set."""

    bbox_filter_field = "city"
    filter_backends = (filters.InBBoxFilter,)
    queryset = Agenda.objects.all()
    serializer_class = AgendaFreeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        print("maps.viewset.AgendaFreeViewSet")
        # print("filter_queryset self.request.GET", self.request.GET)
        date_in = self.request.GET.get("date_in", "")
        date_out = self.request.GET.get("date_out", "")
        if date_in == "" or date_out == "":
            return Agenda.objects.none()
        company_id = self.request.session["company_id"]
        favorite = self.request.GET.get("favorite", False)

        try:
            days_input = int(self.request.GET.get("days", 0))
        except:  # se days_input diverso da intero
            days_input = 0

        qs = self.request.GET.getlist("search", "")
        bbox = self.request.GET.get("in_bbox", "").split(",")
        geom = Polygon.from_bbox(bbox)
        queryset = Agenda.objects.filter(
            user__jobprofile__job__title__in=qs,
            city__within=geom,
            busy=False
        ).distinct()

        # todo: aggiungere i giorni extra. Vedi AgendaBusyViewSet2
        if date_in and date_out:
            date_in_obj = datetime.datetime.strptime(date_in, '%Y-%m-%d').date()
            date_out_obj = datetime.datetime.strptime(date_out, '%Y-%m-%d').date()
            days = datetime.timedelta(days_input)
            date_in_obj_extra = date_in_obj - days
            date_out_obj_extra = date_out_obj + days
            queryset = queryset.filter(
                date_start__date__gte=date_in_obj_extra,
                date_end__date__lte=date_out_obj_extra,
            )
        if favorite == 'true':
            queryset = queryset.filter(user__favorite_company__id=company_id)
        elif favorite == 'false':
            queryset = queryset.exclude(user__favorite_company__id=company_id)
        # print("queryset", queryset)
        return queryset


class AgendaBusyViewSet(viewsets.ReadOnlyModelViewSet):
    """Marker JAgenda view set."""

    bbox_filter_field = "city"
    filter_backends = (filters.InBBoxFilter,)
    queryset = Agenda.objects.none()
    serializer_class = AgendaBusySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # print("maps.viewset.AgendaBusyViewSet")
        # print("filter_queryset self.request.GET", self.request.GET)
        date_in = self.request.GET.get("date_in", "")
        date_out = self.request.GET.get("date_out", "")
        if date_in == "" or date_out == "":
            return Agenda.objects.none()
        company_id = self.request.session["company_id"]
        qs = self.request.GET.get("search", "")

        try:
            days_input = int(self.request.GET.get("days", 0))
        except:  # se days_input diverso da intero
            days_input = 0
        if days_input <= 0:
            return Agenda.objects.none()
        favorite = self.request.GET.get("favorite", False)
        date_in = self.request.GET.get("date_in", "")
        date_out = self.request.GET.get("date_out", "")
        queryset = Agenda.objects.filter(user__jobprofile__job__title=qs, busy=True)
        # print("date_in_obj", date_in)
        # print("date_in_obj", date_out)
        # print(days_input, type(days_input))
        if date_in != "" and date_out != "" and days_input > 0:
            date_in_obj = datetime.datetime.strptime(date_in, '%Y-%m-%d').date()
            date_out_obj = datetime.datetime.strptime(date_out, '%Y-%m-%d').date()
            days = datetime.timedelta(days_input)
            date_in_obj_extra = date_in_obj - days
            date_out_obj_extra = date_out_obj + days
            # print("date_in_obj_extra", date_in_obj_extra)
            # print("date_in_obj", date_in_obj)
            # print("date_in_obj", date_out_obj)
            # print("date_out_obj_extra", date_out_obj_extra)
            queryset = queryset.filter(
                Q(date_start__date__gte=date_in_obj_extra, date_end__date__lt=date_in_obj) |
                Q(date_start__date__gt=date_out_obj, date_end__date__lte=date_out_obj_extra),
            )

        if favorite == 'true':
            queryset = queryset.filter(user__favorite_company__id=company_id)
        elif favorite == 'false':
            queryset = queryset.exclude(user__favorite_company__id=company_id)
        # print("queryset", queryset)
        return queryset


class AgendaBusyViewSet2(viewsets.ReadOnlyModelViewSet):
    """Marker JAgenda view set."""

    bbox_filter_field = "city"
    filter_backends = (filters.InBBoxFilter,)
    queryset = Agenda.objects.none()
    serializer_class = AgendaBusySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # print("maps.viewset.AgendaBusyViewSet")
        # print("filter_queryset self.request.GET", self.request.GET)
        date_in = self.request.GET.get("date_in", "")
        date_out = self.request.GET.get("date_out", "")
        if date_in == "" or date_out == "":
            return Agenda.objects.none()
        company_id = self.request.session["company_id"]

        try:
            days_input = int(self.request.GET.get("days", 0))
        except:  # se days_input diverso da intero
            days_input = 0
        if days_input <= 0:
            return Agenda.objects.none()

        favorite = self.request.GET.get("favorite", False)
        date_in = self.request.GET.get("date_in", "")
        date_out = self.request.GET.get("date_out", "")

        qs = self.request.GET.getlist("search", "")
        bbox = self.request.GET.get("in_bbox", "").split(",")
        geom = Polygon.from_bbox(bbox)
        queryset = Agenda.objects.filter(
            user__jobprofile__job__title__in=qs,
            city__within=geom,
            busy=True
        ).distinct()

        # print("date_in_obj", date_in)
        # print("date_in_obj", date_out)
        # print(days_input, type(days_input))
        if date_in != "" and date_out != "" and days_input > 0:
            date_in_obj = datetime.datetime.strptime(date_in, '%Y-%m-%d').date()
            date_out_obj = datetime.datetime.strptime(date_out, '%Y-%m-%d').date()
            days = datetime.timedelta(days_input)
            date_in_obj_extra = date_in_obj - days
            date_out_obj_extra = date_out_obj + days
            # print("date_in_obj_extra", date_in_obj_extra)
            # print("date_in_obj", date_in_obj)
            # print("date_in_obj", date_out_obj)
            # print("date_out_obj_extra", date_out_obj_extra)
            queryset = queryset.filter(
                Q(date_start__date__gte=date_in_obj_extra, date_end__date__lt=date_in_obj) |
                Q(date_start__date__gt=date_out_obj, date_end__date__lte=date_out_obj_extra),
            )

        if favorite == 'true':
            queryset = queryset.filter(user__favorite_company__id=company_id)
        elif favorite == 'false':
            queryset = queryset.exclude(user__favorite_company__id=company_id)
        # print("queryset", queryset)
        return queryset
