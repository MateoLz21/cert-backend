from rest_framework import status as http_status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.accounts.permissions import IsAdmin, IsAdminOrOwner

from apps.scheduling.models import AvailabilitySlot
from apps.scheduling.services import SchedulingService

from .models import AuditRequest
from .serializers import AuditRequestSerializer
from .services import AuditRequestService


class AuditRequestViewSet(viewsets.ModelViewSet):
    """CRUD de solicitudes de auditoría.

    Los administradores gestionan todas las solicitudes; un cliente solo ve y
    crea las de sus propias empresas. La creación delega en
    ``AuditRequestService`` para generar el código y reservar la franja.
    """

    queryset = AuditRequest.objects.select_related("company", "service", "slot").all()
    serializer_class = AuditRequestSerializer
    permission_classes = [IsAdminOrOwner]

    filterset_fields = ["status", "company", "service"]
    search_fields = ["code", "notes"]
    ordering_fields = ["created_at", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = AuditRequest.objects.select_related(
            "company", "service", "slot"
        ).all()
        user = self.request.user
        if getattr(user, "is_admin", False):
            return queryset
        return queryset.filter(company__user=user)

    def get_object_owner(self, obj):
        return obj.company.user

    def perform_destroy(self, instance):
        """Release the booked slot before deleting the request."""
        slot = instance.slot
        instance.delete()
        if slot and slot.status == AvailabilitySlot.SlotStatus.BOOKED:
            SchedulingService.release_slot(slot)

    def perform_create(self, serializer):
        user = self.request.user
        company = serializer.validated_data["company"]
        if not getattr(user, "is_admin", False) and company.user_id != user.id:
            raise PermissionDenied(
                "No puedes crear solicitudes para esta empresa."
            )
        try:
            instance = AuditRequestService.create_request(
                company=company,
                service=serializer.validated_data["service"],
                slot=serializer.validated_data.get("slot"),
                notes=serializer.validated_data.get("notes", ""),
            )
        except ValueError as exc:
            raise ValidationError({"slot": str(exc)})
        serializer.instance = instance

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def set_status(self, request, pk=None):
        """Cambia el estado de la solicitud (solo administradores)."""
        audit_request = self.get_object()
        new_status = request.data.get("status")
        valid = {choice.value for choice in AuditRequest.Status}
        if new_status not in valid:
            raise ValidationError(
                {"status": f"Estado inválido. Opciones: {sorted(valid)}."}
            )
        audit_request.status = new_status
        audit_request.save(update_fields=["status", "updated_at"])
        serializer = self.get_serializer(audit_request)
        return Response(serializer.data, status=http_status.HTTP_200_OK)
