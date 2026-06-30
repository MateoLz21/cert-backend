"""User and Profile models.

The project uses a custom user model with email as the login identifier and a
UUID primary key, plus a role field driving authorization across the API.
"""
import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user authenticated by email."""

    class Role(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Administrador"
        ADMIN = "admin", "Administrador"
        CLIENT = "client", "Cliente"

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID"
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.CLIENT
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    @property
    def is_admin(self):
        return self.role in {self.Role.ADMIN, self.Role.SUPER_ADMIN}


class Profile(models.Model):
    """Additional per-user information (1:1 with User)."""

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID"
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    phone = models.CharField(max_length=30, blank=True)
    avatar = models.URLField(blank=True)
    document_id = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return f"Perfil de {self.user.email}"
