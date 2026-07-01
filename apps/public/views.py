"""Vistas del sitio web público y la gestión de solicitudes web."""
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdmin
from apps.audit_requests.models import AuditRequest
from apps.scheduling.models import AvailabilitySlot
from apps.services.models import Service

from .models import AuditLead
from .serializers import (
    AuditLeadSerializer,
    CheckoutSerializer,
    LeadStatusSerializer,
    VerifyResultSerializer,
)
from .services import CheckoutService, LeadConversionService


class PublicLeadCreateView(CreateAPIView):
    """Recibe solicitudes desde los formularios de la web pública."""

    serializer_class = AuditLeadSerializer
    permission_classes = [permissions.AllowAny]
    queryset = AuditLead.objects.all()


class VerifyByCodeView(APIView):
    """Verifica un informe de auditoría por su código (público)."""

    permission_classes = [permissions.AllowAny]

    @extend_schema(responses=VerifyResultSerializer)
    def get(self, request, code):
        try:
            audit = AuditRequest.objects.select_related("company", "service", "slot").get(
                code=code
            )
        except AuditRequest.DoesNotExist:
            return Response(
                {"detail": "No se encontró un informe con ese código."},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = {
            "code": audit.code,
            "status": audit.status,
            "status_display": audit.get_status_display(),
            "service_name": audit.service.name,
            "company_business_name": audit.company.business_name,
            "audit_date": audit.slot.date if audit.slot else None,
        }
        return Response(VerifyResultSerializer(data).data)


class CheckoutView(APIView):
    """Inicia una reserva con pago: crea la solicitud y la sesión de Stripe."""

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=CheckoutSerializer,
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="CheckoutResponse",
                    fields={
                        "checkout_url": serializers.URLField(),
                        "code": serializers.CharField(),
                    },
                ),
                description="URL de pago de Stripe.",
            )
        },
    )
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            result = CheckoutService.create_session(
                service=data["service"],
                slot_id=data.get("slot"),
                full_name=data["full_name"],
                ruc=data["ruc"],
                email=data["email"],
                phone=data.get("phone", ""),
            )
        except Exception as exc:  # noqa: BLE001 - surface gateway/config errors
            return Response(
                {"detail": f"No se pudo iniciar el pago: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(result, status=status.HTTP_200_OK)


class StripeWebhookView(APIView):
    """Recibe eventos de Stripe y confirma los pagos completados."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        try:
            event = CheckoutService.construct_event(request.body, sig_header)
        except Exception:  # noqa: BLE001 - invalid signature/payload
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            CheckoutService.fulfill(session["id"])
        return Response({"received": True}, status=status.HTTP_200_OK)


class LeadViewSet(viewsets.ModelViewSet):
    """Gestión de solicitudes web desde el dashboard (solo administradores)."""

    queryset = AuditLead.objects.select_related("audit_request").all()
    serializer_class = AuditLeadSerializer
    permission_classes = [IsAdmin]
    http_method_names = ["get", "patch", "post", "delete", "head", "options"]

    filterset_fields = ["kind", "status"]
    search_fields = ["full_name", "ruc", "email"]
    ordering_fields = ["created_at", "status"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return LeadStatusSerializer
        return AuditLeadSerializer

    @extend_schema(
        request=inline_serializer(
            name="LeadConvertRequest",
            fields={
                "service": serializers.UUIDField(),
                "slot": serializers.UUIDField(required=False),
            },
        ),
        responses={201: OpenApiResponse(description="Solicitud de auditoría creada.")},
    )
    @action(detail=True, methods=["post"])
    def convert(self, request, pk=None):
        """Convierte la solicitud web en una solicitud de auditoría formal."""
        lead = self.get_object()
        service_id = request.data.get("service")
        slot_id = request.data.get("slot")
        if not service_id:
            return Response(
                {"service": "Selecciona un servicio para convertir."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = Service.objects.filter(pk=service_id).first()
        if not service:
            return Response(
                {"service": "Servicio no encontrado."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        slot = AvailabilitySlot.objects.filter(pk=slot_id).first() if slot_id else None
        try:
            audit = LeadConversionService.convert(lead, service, slot)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"audit_request": str(audit.id), "code": audit.code},
            status=status.HTTP_201_CREATED,
        )
