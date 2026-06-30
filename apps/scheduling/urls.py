from rest_framework.routers import DefaultRouter

from .views import AvailabilitySlotViewSet

app_name = "scheduling"

router = DefaultRouter()
router.register(r"", AvailabilitySlotViewSet, basename="slot")

urlpatterns = router.urls
