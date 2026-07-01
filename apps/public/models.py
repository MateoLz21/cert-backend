"""Modelos del sitio web público.

Las solicitudes enviadas desde la web pública (coordinación de auditoría,
cotización o contacto) se guardan como ``AuditLead`` y se revisan desde el
dashboard, donde un administrador puede convertirlas en una solicitud formal.
"""
from django.db import models

from apps.core.models import BaseModel


class AuditLead(BaseModel):
    """Solicitud enviada desde un formulario de la web pública."""

    class Kind(models.TextChoices):
        COORDINATION = "coordination", "Coordinación de auditoría"
        QUOTE = "quote", "Cotización"
        CONTACT = "contact", "Contacto"

    class AuditType(models.TextChoices):
        VIRTUAL = "virtual", "Virtual"
        ON_SITE = "presencial", "Presencial"

    class Status(models.TextChoices):
        NEW = "new", "Nueva"
        CONTACTED = "contacted", "Contactada"
        CONVERTED = "converted", "Convertida"
        CLOSED = "closed", "Cerrada"

    kind = models.CharField(
        "Tipo", max_length=20, choices=Kind.choices
    )
    full_name = models.CharField("Nombres", max_length=255)
    email = models.EmailField("Correo", blank=True)
    phone = models.CharField("Teléfono", max_length=30, blank=True)
    ruc = models.CharField("RUC", max_length=11, blank=True)
    position = models.CharField("Cargo", max_length=150, blank=True)
    sedes = models.CharField("Sedes", max_length=255, blank=True)
    audit_type = models.CharField(
        "Tipo de auditoría",
        max_length=20,
        choices=AuditType.choices,
        blank=True,
    )
    message = models.TextField("Mensaje", blank=True)
    status = models.CharField(
        "Estado",
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    audit_request = models.ForeignKey(
        "audit_requests.AuditRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
        verbose_name="Solicitud generada",
    )

    class Meta:
        verbose_name = "Solicitud web"
        verbose_name_plural = "Solicitudes web"

    def __str__(self):
        return f"{self.get_kind_display()} · {self.full_name}"
