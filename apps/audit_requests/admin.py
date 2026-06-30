from django.contrib import admin

from .models import AuditRequest


@admin.register(AuditRequest)
class AuditRequestAdmin(admin.ModelAdmin):
    list_display = ("code", "company", "service", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("code",)
    readonly_fields = ("code",)
