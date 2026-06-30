import datetime

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import AuditRequest


class AuditRequestSerializer(serializers.ModelSerializer):
    """Serializador para las solicitudes de auditoría."""

    audit_date = serializers.SerializerMethodField()
    audit_time = serializers.SerializerMethodField()

    class Meta:
        model = AuditRequest
        fields = [
            "id",
            "code",
            "company",
            "service",
            "slot",
            "status",
            "notes",
            "audit_date",
            "audit_time",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "code",
            "status",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(serializers.DateField(allow_null=True))
    def get_audit_date(self, obj) -> datetime.date | None:
        """Devuelve la fecha de la franja horaria asociada, o None."""
        return obj.slot.date if obj.slot else None

    @extend_schema_field(serializers.TimeField(allow_null=True))
    def get_audit_time(self, obj) -> datetime.time | None:
        """Devuelve la hora de inicio de la franja horaria asociada, o None."""
        return obj.slot.start_time if obj.slot else None
