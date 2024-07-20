from django.contrib import admin

from .. import models

@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "course_group",
        "description",
        "course_fee",
        "min_students",
        "max_students",
        "next_class",
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