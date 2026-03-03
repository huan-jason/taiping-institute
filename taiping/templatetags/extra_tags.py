from typing import Any
from markdown import markdown  # type: ignore

from django import template
from django.contrib.auth.models import User
from django.utils.html import mark_safe  # type: ignore

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
