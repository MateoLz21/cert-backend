"""Modelos de empresas clientes.

Una empresa representa a la organización cliente que contrata los servicios de
certificación. Opcionalmente puede vincularse a un usuario del sistema.
"""
from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class Company(BaseModel):
    """Empresa cliente que contrata servicios de certificación."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="companies",
    )
    business_name = models.CharField(max_length=255)  # Razón social
    ruc = models.CharField(max_length=11, unique=True)
    address = models.CharField(max_length=255)
    legal_representative = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    business_sector = models.CharField(max_length=150)  # Rubro
    employee_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.business_name
