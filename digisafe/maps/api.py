"""Markers API URL Configuration."""

from rest_framework import routers

from .viewsets import AgendaFreeViewSet, JobViewSet, DefaultPositionViewSet, AgendaBusyViewSet

router = routers.DefaultRouter()
router.register(r"defaultposition", DefaultPositionViewSet)
router.register(r"agendafree", AgendaFreeViewSet)
router.register(r"agendabusy", AgendaBusyViewSet)
router.register(r"search_job", JobViewSet)

urlpatterns = router.urls