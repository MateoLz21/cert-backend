from django.db import models

from apps.core.models import BaseModel


class AuditRequest(BaseModel):
    """Solicitud de auditoría realizada por una empresa para un servicio."""

    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending_payment", "Pendiente de pago"
        PAID = "paid", "Pagada"
        CONFIRMED = "confirmed", "Confirmada"
        SCHEDULED = "scheduled", "Programada"
        FINISHED = "finished", "Finalizada"
        CANCELLED = "cancelled", "Cancelada"

    code = models.CharField(
        "Código",
        max_length=30,
        unique=True,
        editable=False,
    )
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.PROTECT,
        related_name="audit_requests",
        verbose_name="Empresa",
    )
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.PROTECT,
        related_name="audit_requests",
        verbose_name="Servicio",
    )
    slot = models.OneToOneField(
        "scheduling.AvailabilitySlot",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="audit_request",
        verbose_name="Franja horaria",
    )
    status = models.CharField(
        "Estado",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING_PAYMENT,
    )
    notes = models.TextField("Notas", blank=True)

    class Meta:
        verbose_name = "Solicitud de auditoría"
        verbose_name_plural = "Solicitudes de auditoría"

    def __str__(self):
        return self.code
