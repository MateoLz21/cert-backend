from django.contrib import admin

from .models import AvailabilitySlot


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ("date", "start_time", "end_time", "status")
    list_filter = ("status", "date")
    ordering = ("date", "start_time")
