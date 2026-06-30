from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Serializador para pagos."""

    class Meta:
        model = Payment
        fields = [
            "id",
            "audit_request",
            "amount",
            "payment_method",
            "status",
            "paid_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
