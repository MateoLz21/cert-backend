"""Tests for the custom User model and manager."""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_create_user_defaults_to_client_role():
    user = User.objects.create_user(email="cliente@test.com", password="pass12345")
    assert user.email == "cliente@test.com"
    assert user.role == User.Role.CLIENT
    assert user.is_staff is False
    assert user.check_password("pass12345")


@pytest.mark.django_db
def test_create_superuser_is_super_admin():
    admin = User.objects.create_superuser(email="admin@test.com", password="pass12345")
    assert admin.role == User.Role.SUPER_ADMIN
    assert admin.is_staff is True
    assert admin.is_superuser is True
    assert admin.is_admin is True


@pytest.mark.django_db
def test_email_is_required():
    with pytest.raises(ValueError):
        User.objects.create_user(email="", password="pass12345")
