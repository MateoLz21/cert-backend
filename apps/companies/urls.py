"""Rutas de empresas (montadas bajo /api/v1/companies/)."""
from rest_framework.routers import DefaultRouter

from .views import CompanyViewSet

app_name = "companies"

router = DefaultRouter()
router.register(r"", CompanyViewSet, basename="company")

urlpatterns = router.urls
