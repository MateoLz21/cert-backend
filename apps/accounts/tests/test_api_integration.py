"""Integration checks for the frontend-driven API extensions.

Exercises client self-service scoping, the audit-request creation flow,
user management permissions, and server-side filtering.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.companies.models import Company
from apps.services.models import Service
from apps.scheduling.models import AvailabilitySlot

User = get_user_model()


def make_client(user):
    api = APIClient()
    api.force_authenticate(user=user)
    return api


@pytest.fixture
def users(db):
    return {
        "super": User.objects.create_superuser("super@t.com", "pass12345"),
        "admin": User.objects.create_user(
            "admin@t.com", "pass12345", role=User.Role.ADMIN
        ),
        "c1": User.objects.create_user("c1@t.com", "pass12345"),
        "c2": User.objects.create_user("c2@t.com", "pass12345"),
    }


def company_payload(**over):
    data = {
        "business_name": "ACME",
        "ruc": "12345678901",
        "address": "Av 1",
        "legal_representative": "Rep",
        "contact_person": "Contacto",
        "email": "a@a.com",
        "phone": "999",
        "business_sector": "TI",
        "employee_count": 5,
    }
    data.update(over)
    return data


@pytest.mark.django_db
def test_company_scoped_to_owner(users):
    c1 = make_client(users["c1"])
    res = c1.post("/api/v1/companies/", company_payload(), format="json")
    assert res.status_code == 201, res.content
    # Owner auto-assigned, not client-controlled.
    assert Company.objects.get().user_id == users["c1"].id

    # c2 sees nothing; admin sees all.
    assert make_client(users["c2"]).get("/api/v1/companies/").data["count"] == 0
    assert make_client(users["admin"]).get("/api/v1/companies/").data["count"] == 1


@pytest.mark.django_db
def test_audit_request_create_generates_code_and_scopes(users):
    company = Company.objects.create(user=users["c1"], **company_payload(ruc="20000000001"))
    service = Service.objects.create(
        name="ISO 9001", price="1000.00", estimated_duration="08:00:00"
    )
    slot = AvailabilitySlot.objects.create(
        date="2026-07-01", start_time="09:00", end_time="17:00"
    )
    c1 = make_client(users["c1"])
    res = c1.post(
        "/api/v1/audit-requests/",
        {"company": str(company.id), "service": str(service.id), "slot": str(slot.id)},
        format="json",
    )
    assert res.status_code == 201, res.content
    assert res.data["code"].startswith("AUD-")
    assert res.data["status"] == "scheduled"  # slot booked => scheduled
    # c2 cannot create for c1's company.
    res2 = make_client(users["c2"]).post(
        "/api/v1/audit-requests/",
        {"company": str(company.id), "service": str(service.id)},
        format="json",
    )
    assert res2.status_code in (403, 400)


@pytest.mark.django_db
def test_users_crud_permissions(users):
    # Client forbidden to list users.
    assert make_client(users["c1"]).get("/api/v1/users/").status_code == 403
    # Admin may list but not create.
    assert make_client(users["admin"]).get("/api/v1/users/").status_code == 200
    res_admin_create = make_client(users["admin"]).post(
        "/api/v1/users/",
        {"email": "x@t.com", "password": "pass12345", "role": "admin"},
        format="json",
    )
    assert res_admin_create.status_code == 403
    # Super admin creates with role.
    res = make_client(users["super"]).post(
        "/api/v1/users/",
        {"email": "newadmin@t.com", "password": "pass12345", "role": "admin"},
        format="json",
    )
    assert res.status_code == 201, res.content
    assert res.data["role"] == "admin"
    assert User.objects.get(email="newadmin@t.com").check_password("pass12345")


@pytest.mark.django_db
def test_service_is_active_filter(users):
    Service.objects.create(name="A", price="1", estimated_duration="01:00:00", is_active=True)
    Service.objects.create(name="B", price="1", estimated_duration="01:00:00", is_active=False)
    api = make_client(users["admin"])
    assert api.get("/api/v1/services/?is_active=true").data["count"] == 1
    assert api.get("/api/v1/services/?is_active=false").data["count"] == 1
