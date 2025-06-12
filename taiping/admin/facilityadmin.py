from django.contrib import admin

from .. import models


@admin.register(models.Facility)
class FacilityAdmin(admin.ModelAdmin):

    list_display = [
        "name",
        "contact_name",
        "contact_phone",
        "contact_email",
        "approved",
    ]
    list_filter = [
        "approved",
    ]
    search_fields = [
        "name",
        "description",
        "address"
        "contact_name",
    ]
    ordering = [
        "name",
    ]
