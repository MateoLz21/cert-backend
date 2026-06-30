from rest_framework.routers import DefaultRouter

from .views import AuditRequestViewSet

app_name = "audit_requests"

router = DefaultRouter()
router.register(r"", AuditRequestViewSet, basename="audit-request")

urlpatterns = router.urls
