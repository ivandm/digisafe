"""Markers API URL Configuration."""

from rest_framework import routers

from .viewsets import JobViewSet, DefaultPositionViewSet, \
    DefaultPositionViewSet2, AgendaBusyViewSet, AgendaFreeViewSet, AgendaBusyViewSet2, AgendaFreeViewSet2

router = routers.DefaultRouter()
router.register(r"defaultposition", DefaultPositionViewSet)
router.register(r"defaultposition2", DefaultPositionViewSet2)
router.register(r"agendafree", AgendaFreeViewSet)
router.register(r"agendafree2", AgendaFreeViewSet2)
router.register(r"agendabusy", AgendaBusyViewSet)
router.register(r"agendabusy2", AgendaBusyViewSet2)
router.register(r"search_job", JobViewSet)

urlpatterns = router.urls