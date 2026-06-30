"""Configuración del panel de administración de servicios."""
from django.contrib import admin

from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Administración de los servicios de auditoría."""

    list_display = ("name", "price", "estimated_duration", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
