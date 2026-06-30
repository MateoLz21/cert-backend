from rest_framework import serializers

from .models import AvailabilitySlot


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    """Serializador para los slots de disponibilidad."""

    class Meta:
        model = AvailabilitySlot
        fields = [
            "id",
            "date",
            "start_time",
            "end_time",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        """Valida que la hora de fin sea posterior a la hora de inicio."""
        start_time = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end_time = attrs.get("end_time", getattr(self.instance, "end_time", None))
        if start_time is not None and end_time is not None and end_time <= start_time:
            raise serializers.ValidationError(
                "La hora de fin debe ser posterior a la hora de inicio."
            )
        return attrs
