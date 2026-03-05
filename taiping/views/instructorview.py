from typing import Any, cast

from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from taiping.models import Instructor


class InstructorView(View):

    def get(self, request: HttpRequest) -> HttpResponse:

        if htmx := request.GET.get("htmx"):
            return getattr(self, f"htmx_{htmx.replace('-', '_')}")(request)

        user: User = cast(Any, request.user)
        instructor: Instructor | None = getattr(request.user, "instructor", None)
        name: str = user.get_full_name()
        name_alt: str = instructor.alternative_name if instructor else ""  # type: ignore
        background_char: str = "教"
        current_tab: str = "instructor"
        title: str = "<em>Instructor</em> Dashboard"
        subtitle: str = (
            f"{name}" +
            (f"&nbsp;/&nbsp; {name_alt}" if name_alt else "")
        )
        return render(request, "agojin/instructor/index.html", locals())

    def htmx_overview(self, request: HttpRequest) -> HttpResponse:
        return render(request, "agojin/instructor/overview.html", locals())

    def htmx_enrolled_students(self, request: HttpRequest) -> HttpResponse:
        return HttpResponse("htmx_enrolled_students")

    def htmx_manage_courses(self, request: HttpRequest) -> HttpResponse:
        return HttpResponse("htmx_manage_courses")

    def htmx_revenue(self, request: HttpRequest) -> HttpResponse:
        return HttpResponse("htmx_revenue")

    def htmx_schedule(self, request: HttpRequest) -> HttpResponse:
        return HttpResponse("htmx_schedule")

    def htmx_stats(self, request: HttpRequest) -> HttpResponse:
        return HttpResponse("htmx_stats")
