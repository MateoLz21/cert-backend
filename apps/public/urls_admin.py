"""Rutas de gestión de solicitudes web (montadas bajo /api/v1/leads/)."""
from rest_framework.routers import DefaultRouter

from .views import LeadViewSet

app_name = "leads"

router = DefaultRouter()
router.register(r"", LeadViewSet, basename="lead")

urlpatterns = router.urls
