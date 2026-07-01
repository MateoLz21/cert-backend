"""Serializers del sitio web público."""
from rest_framework import serializers

from apps.services.models import Service

from .models import AuditLead


class AuditLeadSerializer(serializers.ModelSerializer):
    """Crea y expone solicitudes web. ``status`` lo gestiona el dashboard."""

    class Meta:
        model = AuditLead
        fields = [
            "id",
            "kind",
            "full_name",
            "email",
            "phone",
            "ruc",
            "position",
            "sedes",
            "audit_type",
            "message",
            "status",
            "audit_request",
            "created_at",
        ]
        read_only_fields = ["id", "status", "audit_request", "created_at"]


class LeadStatusSerializer(serializers.ModelSerializer):
    """Actualización restringida del estado desde el dashboard."""

    class Meta:
        model = AuditLead
        fields = ["status"]


class VerifyResultSerializer(serializers.Serializer):
    """Información pública de un informe verificado por código."""

    code = serializers.CharField()
    status = serializers.CharField()
    status_display = serializers.CharField()
    service_name = serializers.CharField()
    company_business_name = serializers.CharField()
    audit_date = serializers.DateField(allow_null=True)


class CheckoutSerializer(serializers.Serializer):
    """Datos para iniciar una reserva con pago desde la web pública."""

    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.filter(is_active=True)
    )
    slot = serializers.UUIDField(required=False, allow_null=True)
    full_name = serializers.CharField(max_length=255)
    ruc = serializers.CharField(max_length=11)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=30, required=False, allow_blank=True)
