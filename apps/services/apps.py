"""Configuración de la app de servicios de auditoría."""
from django.apps import AppConfig


class ServicesConfig(AppConfig):
    """Configuración de la aplicación ``services``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.services"
    verbose_name = "Servicios de Auditoría"
