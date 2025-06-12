from django.contrib import admin

from .. import models


@admin.register(models.Instructor)
class InstructorAdmin(admin.ModelAdmin):

    list_display = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "verified",
        "calendar_sync",
        "date_joined",
    ]
    list_filter = [
        "verified",
    ]
    search_fields = [
        "bio",
        "certifications",
    ]
    ordering = [
        "user__username",
    ]
