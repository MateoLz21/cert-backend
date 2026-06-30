from django.db import transaction

from .models import AvailabilitySlot


class SchedulingService:
    """Servicio con la lógica de negocio para la gestión de la agenda."""

    @staticmethod
    def book_slot(slot_id):
        """Reserva un slot de disponibilidad de forma atómica.

        Bloquea el registro con select_for_update para evitar reservas
        concurrentes. Si el slot no está disponible, lanza ValueError.
        """
        with transaction.atomic():
            slot = AvailabilitySlot.objects.select_for_update().get(pk=slot_id)
            if slot.status != AvailabilitySlot.SlotStatus.AVAILABLE:
                raise ValueError("Slot no disponible")
            slot.status = AvailabilitySlot.SlotStatus.BOOKED
            slot.save()
            return slot

    @staticmethod
    def release_slot(slot):
        """Libera un slot, dejándolo nuevamente disponible."""
        slot.status = AvailabilitySlot.SlotStatus.AVAILABLE
        slot.save()
        return slot
