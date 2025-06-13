from typing import Any, Self, cast
from django.contrib import admin

from .. import models


@admin.register(models.CourseClass)
class CourseClassAdmin(admin.ModelAdmin):

    list_display = [
        "course__name",
        "start_date",
        "end_date",
        "status",
        "started",
        "auto_start",
        "instructor",
        "facility",
        "course_fee",
        "min_students",
        "max_students",
    ]
    list_filter = [
        "course__name",
        "instructor",
        "facility",
        "status",
        "start_date",
        "end_date",
        "started",
        "auto_start",
    ]
    ordering = [
        "start_date",
        "course__name",
        "end_date",
    ]

    def course_fee(self, obj: models.CourseClass) -> int:
        return cast(Any, obj.course_fee or obj.course.course_fee)

    def min_students(self, obj: models.CourseClass) -> int:
        return cast(Any, obj.min_students or obj.course.min_students)

    def max_students(self, obj: models.CourseClass) -> int:
        return cast(Any, obj.max_students or obj.course.max_students)

    def instructor(self, obj: models.CourseClass) -> str:
        return cast(Any, obj.instructor or obj.course.instructor).get_full_name()

    def facility(self, obj: models.CourseClass) -> str:
        return cast(Any, obj.facility or obj.course.facility).name

