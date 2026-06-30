from django.db import transaction
from django.utils import timezone

from .models import AuditRequest


class AuditRequestService:
    """Lógica de negocio para la creación de solicitudes de auditoría."""

    @staticmethod
    def generate_code():
        """Genera un código secuencial con el formato 'AUD-<año>-<secuencial>'."""
        year = timezone.now().year
        count = AuditRequest.objects.filter(code__startswith=f"AUD-{year}-").count() + 1
        return f"AUD-{year}-{count:04d}"

    @staticmethod
    @transaction.atomic
    def create_request(company, service, slot=None, notes=""):
        """Crea una solicitud de auditoría.

        Si se proporciona una franja horaria, se reserva mediante el servicio
        de agendamiento y la solicitud queda en estado 'Programada'. En caso
        contrario, la solicitud queda 'Pendiente de pago'.
        """
        status = AuditRequest.Status.PENDING_PAYMENT
        if slot is not None:
            from apps.scheduling.services import SchedulingService

            SchedulingService.book_slot(slot.id)
            status = AuditRequest.Status.SCHEDULED

        code = AuditRequestService.generate_code()
        return AuditRequest.objects.create(
            code=code,
            company=company,
            service=service,
            slot=slot,
            status=status,
            notes=notes,
        )
