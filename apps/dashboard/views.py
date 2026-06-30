from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdmin

from .services import DashboardService


class DashboardStatsView(APIView):
    """Devuelve estadísticas básicas agregadas para el panel administrativo."""

    permission_classes = [IsAdmin]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Estadísticas agregadas de la plataforma.",
            )
        }
    )
    def get(self, request):
        return Response(DashboardService.get_basic_stats())
