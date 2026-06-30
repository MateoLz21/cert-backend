"""API views para la gestión de empresas clientes."""
from rest_framework.viewsets import ModelViewSet

from apps.accounts.permissions import IsAdminOrOwner

from .models import Company
from .serializers import CompanySerializer


class CompanyViewSet(ModelViewSet):
    """CRUD de empresas clientes.

    Los administradores gestionan todas las empresas; un cliente solo ve y
    gestiona las suyas, y al crear una se le asigna automáticamente como dueño.
    """

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAdminOrOwner]

    filterset_fields = ["business_sector"]
    search_fields = ["business_name", "ruc", "contact_person"]
    ordering_fields = ["created_at", "business_name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Company.objects.all()
        user = self.request.user
        if getattr(user, "is_admin", False):
            return queryset
        return queryset.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, "is_admin", False):
            serializer.save()
        else:
            serializer.save(user=user)

    def get_object_owner(self, obj):
        return obj.user
