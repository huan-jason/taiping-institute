from django.contrib import admin

from .. import models


@admin.register(models.Compliance)
class ComplianceAdmin(admin.ModelAdmin):
    list_display = [
        "compliance_type",
        "student",
        "created",
    ]
    list_filter = [
        "compliance_type",
    ]
    search_fields = [
        "student__user__email",
    ]
    ordering = [
        "-created",
    ]
