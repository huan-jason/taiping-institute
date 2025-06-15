from django.contrib import admin

from .. import models


@admin.register(models.EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = [
        "email",
        "code",
    ]
    search_fields = [
        "email",
    ]
    ordering = [
        "-created",
    ]
