from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["business_name", "ruc", "business_sector", "employee_count"]
    search_fields = ["business_name", "ruc"]
