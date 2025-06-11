from django.contrib import admin

from .. import models

@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "course_group",
        "description",
    ]
    list_filter = [
        "course_group",
    ]
    search_fields = [
        "name",
        "description",
    ]
    ordering = [
        "sort_order",
    ]