from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "audit_request",
        "amount",
        "payment_method",
        "status",
        "paid_at",
    )
    list_filter = ("status", "payment_method")
