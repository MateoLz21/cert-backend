"""Serializadores de la app de servicios."""
from rest_framework import serializers

from .models import Service


class ServiceSerializer(serializers.ModelSerializer):
    """Serializa los servicios del catálogo de auditoría."""

    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "description",
            "price",
            "estimated_duration",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
