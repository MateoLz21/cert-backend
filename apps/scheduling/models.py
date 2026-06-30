from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import BaseModel


class AvailabilitySlot(BaseModel):
    """Slot de disponibilidad predefinido con capacidad 1."""

    class SlotStatus(models.TextChoices):
        AVAILABLE = "available", "Disponible"
        BLOCKED = "blocked", "Bloqueado"
        BOOKED = "booked", "Reservado"

    date = models.DateField("Fecha")
    start_time = models.TimeField("Hora de inicio")
    end_time = models.TimeField("Hora de fin")
    status = models.CharField(
        "Estado",
        max_length=20,
        choices=SlotStatus.choices,
        default=SlotStatus.AVAILABLE,
    )

    class Meta:
        verbose_name = "Slot de disponibilidad"
        verbose_name_plural = "Slots de disponibilidad"
        ordering = ["date", "start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["date", "start_time", "end_time"],
                name="unique_slot",
            )
        ]

    def clean(self):
        """Valida que la hora de fin sea posterior a la hora de inicio."""
        if self.end_time <= self.start_time:
            raise ValidationError(
                "La hora de fin debe ser posterior a la hora de inicio."
            )

    def __str__(self):
        return f"{self.date} {self.start_time}-{self.end_time}"

    @property
    def is_available(self):
        """Indica si el slot está disponible."""
        return self.status == self.SlotStatus.AVAILABLE
