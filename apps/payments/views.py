from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from apps.accounts.permissions import IsAdminOrOwner

from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """Gestión de pagos.

    Los administradores ven todos los pagos; un cliente solo ve y registra los
    de sus propias solicitudes de auditoría.
    """

    queryset = Payment.objects.select_related("audit_request").all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminOrOwner]

    filterset_fields = ["status", "payment_method", "audit_request"]
    ordering_fields = ["created_at", "amount"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Payment.objects.select_related("audit_request").all()
        user = self.request.user
        if getattr(user, "is_admin", False):
            return queryset
        return queryset.filter(audit_request__company__user=user)

    def get_object_owner(self, obj):
        return obj.audit_request.company.user

    def perform_create(self, serializer):
        user = self.request.user
        audit_request = serializer.validated_data["audit_request"]
        if (
            not getattr(user, "is_admin", False)
            and audit_request.company.user_id != user.id
        ):
            raise PermissionDenied(
                "No puedes registrar pagos para esta solicitud."
            )
        serializer.save()
