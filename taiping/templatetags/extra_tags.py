from typing import Any
from markdown import markdown  # type: ignore

from django import template
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.utils.html import mark_safe  # type: ignore
from taiping.models import (
    Course,
    CourseClassStudent,
    CourseDependency,
)


register = template.Library()


@register.filter
def from_markdown(value: str, *args: Any):
    if value == 'None': return ''
    return mark_safe(markdown(value or ""))


@register.filter
def is_instructor(user: User) -> bool:
    return hasattr(user, "instructor")


@register.filter
def is_student(user: User) -> bool:
    return hasattr(user, "student")


@register.filter
def meets_prerequisites(course: Course, user: User) -> bool:
    dependent_course_ids: list[int] = list(CourseDependency.objects
        .filter(course=course)
        .values_list("dependent_course_id", flat=True)
    )
    student_courses: QuerySet[CourseClassStudent] = (CourseClassStudent.objects
        .filter(course_class__course__in=dependent_course_ids)
    )
    return len(dependent_course_ids) == student_courses.count()
