"""Vistas de la API para el catálogo de servicios."""
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from apps.accounts.permissions import IsAdmin

from .models import Service
from .serializers import ServiceSerializer


class ServiceViewSet(ModelViewSet):
    """Gestiona los servicios del catálogo de auditoría.

    La lectura es pública; la escritura requiere permisos de administrador.
    """

    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    filterset_fields = ["is_active"]
    search_fields = ["name"]
    ordering_fields = ["price", "name"]
    ordering = ["name"]

    def get_permissions(self):
        """Lectura pública; escritura solo para administradores."""
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdmin()]

    def get_queryset(self):
        """Restringe a servicios activos salvo para administradores."""
        queryset = Service.objects.all()
        user = self.request.user
        if user.is_authenticated and getattr(user, "is_admin", False):
            return queryset
        return queryset.filter(is_active=True)
