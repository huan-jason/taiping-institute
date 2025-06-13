from django.contrib import admin

from .. import models


@admin.register(models.Registration)
class RegistrationAdmin(admin.ModelAdmin):

    list_display = [
        "course_class__course__name",
        "course_class__start_date",
        "course_class__end_date",
        "student",
        "started",
        "completed",
    ]
    list_filter = [
        "course_class",
        "student",
        "started",
        "completed",
    ]
    ordering = [
        "course_class__course__name",
        "student__username",
    ]
