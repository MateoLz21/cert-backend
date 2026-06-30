"""Serializers para la app de empresas."""
from rest_framework import serializers

from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "id",
            "user",
            "business_name",
            "ruc",
            "address",
            "legal_representative",
            "contact_person",
            "email",
            "phone",
            "business_sector",
            "employee_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]
