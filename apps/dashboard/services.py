from django.db.models import Sum


class DashboardService:
    """Servicio que agrega datos de otras apps para el panel administrativo."""

    @staticmethod
    def get_basic_stats():
        """Devuelve estadísticas básicas agregadas de las distintas apps.

        Los modelos se importan de forma diferida (lazy) dentro del método
        para evitar problemas de orden de importación entre apps.
        """
        from apps.companies.models import Company
        from apps.services.models import Service
        from apps.audit_requests.models import AuditRequest
        from apps.payments.models import Payment
        from apps.scheduling.models import AvailabilitySlot

        audit_requests_by_status = {
            status.value: AuditRequest.objects.filter(status=status.value).count()
            for status in AuditRequest.Status
        }

        total_paid_amount = (
            Payment.objects.filter(status=Payment.Status.COMPLETED).aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        return {
            "total_companies": Company.objects.count(),
            "total_services": Service.objects.count(),
            "active_services": Service.objects.filter(is_active=True).count(),
            "total_audit_requests": AuditRequest.objects.count(),
            "audit_requests_by_status": audit_requests_by_status,
            "total_payments": Payment.objects.count(),
            "total_paid_amount": total_paid_amount,
            "total_available_slots": AvailabilitySlot.objects.filter(
                status=AvailabilitySlot.SlotStatus.AVAILABLE
            ).count(),
        }
