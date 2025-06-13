from django.contrib import admin

from .. import models


@admin.register(models.CourseDependency)
class CourseDependencyAdmin(admin.ModelAdmin):

    list_display = [
        "course",
        "dependent_course",
    ]
    list_filter = [
        "course",
        "dependent_course",
    ]
    ordering = [
        "course__name",
        "dependent_course__name",
    ]
