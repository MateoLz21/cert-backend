"""Lógica de negocio del sitio web público."""
import stripe
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.audit_requests.models import AuditRequest
from apps.audit_requests.services import AuditRequestService
from apps.companies.models import Company
from apps.payments.models import Payment
from apps.scheduling.models import AvailabilitySlot

from .models import AuditLead


class LeadConversionService:
    """Convierte una solicitud web en una solicitud de auditoría formal."""

    @staticmethod
    @transaction.atomic
    def convert(lead: AuditLead, service, slot=None):
        """Crea (o reutiliza) la empresa por RUC y genera la audit-request.

        La empresa queda como invitada (``user=None``) para que un admin la
        reasigne luego. Marca el lead como convertido y lo enlaza.
        """
        if not lead.ruc:
            raise ValueError("La solicitud no tiene RUC; no se puede convertir.")

        company, _ = Company.objects.get_or_create(
            ruc=lead.ruc,
            defaults={
                "business_name": lead.full_name or lead.ruc,
                "address": "",
                "legal_representative": lead.full_name,
                "contact_person": lead.full_name,
                "email": lead.email,
                "phone": lead.phone,
                "business_sector": "",
            },
        )

        audit_request = AuditRequestService.create_request(
            company=company,
            service=service,
            slot=slot,
            notes=lead.message,
        )

        lead.audit_request = audit_request
        lead.status = AuditLead.Status.CONVERTED
        lead.save(update_fields=["audit_request", "status", "updated_at"])
        return audit_request


class CheckoutService:
    """Reserva con pago en línea mediante Stripe Checkout."""

    @staticmethod
    @transaction.atomic
    def create_session(*, service, slot_id, full_name, ruc, email, phone=""):
        """Crea empresa+solicitud+pago pendientes y una sesión de Stripe.

        Devuelve la URL de pago a la que el frontend debe redirigir.
        """
        slot = None
        if slot_id:
            slot = AvailabilitySlot.objects.filter(
                pk=slot_id, status=AvailabilitySlot.SlotStatus.AVAILABLE
            ).first()

        company, _ = Company.objects.get_or_create(
            ruc=ruc,
            defaults={
                "business_name": full_name or ruc,
                "address": "",
                "legal_representative": full_name,
                "contact_person": full_name,
                "email": email,
                "phone": phone,
                "business_sector": "",
            },
        )

        audit_request = AuditRequestService.create_request(
            company=company, service=service, slot=slot, notes=""
        )
        payment = Payment.objects.create(
            audit_request=audit_request,
            amount=service.price,
            payment_method=Payment.Method.CARD,
            status=Payment.Status.PENDING,
        )

        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": settings.STRIPE_CURRENCY,
                        "unit_amount": int(round(float(service.price) * 100)),
                        "product_data": {"name": service.name},
                    },
                    "quantity": 1,
                }
            ],
            metadata={
                "payment_id": str(payment.id),
                "audit_request_id": str(audit_request.id),
            },
            customer_email=email,
            success_url=(
                f"{settings.FRONTEND_URL}/reserva/exito?code={audit_request.code}"
            ),
            cancel_url=f"{settings.FRONTEND_URL}/reservar",
        )
        payment.external_reference = session.id
        payment.save(update_fields=["external_reference", "updated_at"])
        return {"checkout_url": session.url, "code": audit_request.code}

    @staticmethod
    def construct_event(payload, sig_header):
        """Valida la firma del webhook y devuelve el evento de Stripe."""
        return stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )

    @staticmethod
    @transaction.atomic
    def fulfill(session_id):
        """Marca el pago como completado y avanza la solicitud (idempotente)."""
        payment = (
            Payment.objects.select_for_update()
            .filter(external_reference=session_id)
            .select_related("audit_request")
            .first()
        )
        if not payment or payment.status == Payment.Status.COMPLETED:
            return payment
        payment.status = Payment.Status.COMPLETED
        payment.paid_at = timezone.now()
        payment.save(update_fields=["status", "paid_at", "updated_at"])

        audit = payment.audit_request
        audit.status = AuditRequest.Status.PAID
        audit.save(update_fields=["status", "updated_at"])
        return payment
