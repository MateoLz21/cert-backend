from django.db import models

from apps.core.models import BaseModel


class Payment(BaseModel):
    """Pago asociado a una solicitud de auditoría."""

    class Method(models.TextChoices):
        CARD = "card", "Tarjeta"
        BANK_TRANSFER = "bank_transfer", "Transferencia bancaria"
        CASH = "cash", "Efectivo"
        OTHER = "other", "Otro"

    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        COMPLETED = "completed", "Completado"
        FAILED = "failed", "Fallido"
        REFUNDED = "refunded", "Reembolsado"

    audit_request = models.ForeignKey(
        "audit_requests.AuditRequest",
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="Solicitud de auditoría",
    )
    amount = models.DecimalField(
        "Monto",
        max_digits=10,
        decimal_places=2,
    )
    payment_method = models.CharField(
        "Método de pago",
        max_length=20,
        choices=Method.choices,
    )
    status = models.CharField(
        "Estado",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    paid_at = models.DateTimeField(
        "Fecha de pago",
        null=True,
        blank=True,
    )
    external_reference = models.CharField(
        "Referencia externa",
        max_length=255,
        blank=True,
        help_text="Identificador de la pasarela de pago (p. ej. Stripe session id).",
    )

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        return f"{self.audit_request.code} - {self.amount}"
