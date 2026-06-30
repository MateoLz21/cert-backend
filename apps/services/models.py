"""Modelos del catálogo de servicios de auditoría."""
from django.db import models

from apps.core.models import BaseModel


class Service(BaseModel):
    """Servicio de auditoría ofrecido en el catálogo."""

    name = models.CharField(max_length=255, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio",
    )
    estimated_duration = models.DurationField(
        help_text="Duración estimada de la auditoría",
        verbose_name="Duración estimada",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"

    def __str__(self):
        return self.name
