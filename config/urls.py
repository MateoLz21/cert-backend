"""Root URL configuration.

All API routes are versioned under /api/v1/. API documentation is served by
drf-spectacular (schema + Swagger UI + ReDoc).
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

api_v1_patterns = [
    path("auth/", include("apps.accounts.urls")),
    path("users/", include("apps.accounts.urls_users")),
    path("public/", include("apps.public.urls")),
    path("leads/", include("apps.public.urls_admin")),
    path("companies/", include("apps.companies.urls")),
    path("services/", include("apps.services.urls")),
    path("scheduling/", include("apps.scheduling.urls")),
    path("audit-requests/", include("apps.audit_requests.urls")),
    path("payments/", include("apps.payments.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include((api_v1_patterns, "v1"))),
    # API schema and documentation.
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
