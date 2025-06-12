from django.contrib import admin

from .. import models


class CourseClassInlineAdmin(admin.TabularInline):

    FIELDS = [
        "start_date",
        "end_date",
        "instructor",
        "course_fee",
        "min_students",
        "max_students",
        "facility",
        "status",
        "auto_start",
    ]

    model = models.CourseClass
    extra = 0
    show_change_link = True


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "chinese_name",
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

    inlines = [
        CourseClassInlineAdmin
    ]
