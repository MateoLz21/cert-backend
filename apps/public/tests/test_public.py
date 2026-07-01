"""Tests del sitio web público: leads, verificación, conversión y checkout."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.audit_requests.models import AuditRequest
from apps.companies.models import Company
from apps.payments.models import Payment
from apps.public.models import AuditLead
from apps.scheduling.models import AvailabilitySlot
from apps.services.models import Service

User = get_user_model()


@pytest.fixture
def admin(db):
    return User.objects.create_superuser("super@t.com", "pass12345")


@pytest.fixture
def service(db):
    return Service.objects.create(
        name="Auditoría MINTRA", price="1200.00", estimated_duration="08:00:00"
    )


def admin_client(user):
    api = APIClient()
    api.force_authenticate(user=user)
    return api


@pytest.mark.django_db
def test_public_lead_create_is_open():
    api = APIClient()  # anonymous
    res = api.post(
        "/api/v1/public/leads/",
        {"kind": "quote", "full_name": "Juan", "ruc": "20111111111", "sedes": "2"},
        format="json",
    )
    assert res.status_code == 201, res.content
    assert AuditLead.objects.get().status == "new"


@pytest.mark.django_db
def test_lead_list_requires_admin(admin):
    AuditLead.objects.create(kind="contact", full_name="Ana")
    assert APIClient().get("/api/v1/leads/").status_code == 401
    res = admin_client(admin).get("/api/v1/leads/")
    assert res.status_code == 200
    assert res.data["count"] == 1


@pytest.mark.django_db
def test_lead_convert_creates_audit_request(admin, service):
    lead = AuditLead.objects.create(
        kind="coordination", full_name="Empresa X", ruc="20222222222"
    )
    res = admin_client(admin).post(
        f"/api/v1/leads/{lead.id}/convert/",
        {"service": str(service.id)},
        format="json",
    )
    assert res.status_code == 201, res.content
    lead.refresh_from_db()
    assert lead.status == "converted"
    assert lead.audit_request is not None
    assert Company.objects.filter(ruc="20222222222").exists()


@pytest.mark.django_db
def test_verify_by_code(admin, service):
    company = Company.objects.create(
        business_name="ACME", ruc="20333333333", address="x",
        legal_representative="r", contact_person="c", email="a@a.com",
        phone="9", business_sector="TI",
    )
    audit = AuditRequest.objects.create(code="AUD-2026-0001", company=company, service=service)
    api = APIClient()
    ok = api.get(f"/api/v1/public/verify/{audit.code}/")
    assert ok.status_code == 200
    assert ok.data["service_name"] == "Auditoría MINTRA"
    assert api.get("/api/v1/public/verify/NOPE/").status_code == 404


@pytest.mark.django_db
def test_checkout_creates_pending_order_and_webhook_fulfills(service, monkeypatch):
    slot = AvailabilitySlot.objects.create(
        date="2026-08-01", start_time="09:00", end_time="17:00"
    )

    class FakeSession:
        id = "cs_test_123"
        url = "https://stripe.test/cs_test_123"

    monkeypatch.setattr(
        "apps.public.services.stripe.checkout.Session.create",
        lambda **kwargs: FakeSession(),
    )

    api = APIClient()
    res = api.post(
        "/api/v1/public/checkout/",
        {
            "service": str(service.id),
            "slot": str(slot.id),
            "full_name": "Cliente Web",
            "ruc": "20444444444",
            "email": "web@cliente.com",
        },
        format="json",
    )
    assert res.status_code == 200, res.content
    assert res.data["checkout_url"].startswith("https://stripe.test/")

    payment = Payment.objects.get(external_reference="cs_test_123")
    assert payment.status == "pending"
    slot.refresh_from_db()
    assert slot.status == "booked"  # slot reserved at order creation

    # Simulate the webhook event.
    monkeypatch.setattr(
        "apps.public.services.stripe.Webhook.construct_event",
        lambda payload, sig, secret: {
            "type": "checkout.session.completed",
            "data": {"object": {"id": "cs_test_123"}},
        },
    )
    hook = api.post(
        "/api/v1/public/stripe/webhook/", {}, format="json",
        HTTP_STRIPE_SIGNATURE="t=1,v1=fake",
    )
    assert hook.status_code == 200
    payment.refresh_from_db()
    assert payment.status == "completed"
    assert payment.audit_request.status == "paid"
