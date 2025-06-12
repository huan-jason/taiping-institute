from typing import Any
from markdown import markdown # type: ignore

from django import template
from django.utils.html import mark_safe # type: ignore

register = template.Library()


@register.filter
def from_markdown(value: str, *args: Any):
    return mark_safe(markdown(value))
