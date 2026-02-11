from typing import Any
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from taiping.models import Course
from taiping.utils import get_courses_list_context
from .classschedulemixin import ClassScheduleMixin


class CourseView(ClassScheduleMixin, View):

    def get(self, request: HttpRequest, course_id: int | None = None) -> HttpResponse:

        if name := request.GET.get("htmx"):
            return getattr(self, f"htmx_{name.replace("-", "_")}")(request)

        if course_id:
            return self.get_course_detail(request, course_id=course_id)

        return self.get_courses_list(request)

    def get_course_detail(self, request: HttpRequest, course_id: int) -> HttpResponse:
        course: Course | None = Course.objects.filter(id=course_id).first()
        return (
            render(request, "taiping/course/detail.html", locals())
            if course else
            HttpResponse(f"Invalid course ID: {course_id}", status=400)
        )

    def get_courses_list(self, request: HttpRequest) -> HttpResponse:
        context: dict[str, Any] = get_courses_list_context(request)
        context |= {
            "show_create_course_button": (request.user.groups
                .filter(name="data_admin")
                .exists()
            ),
            "header_title": "The art of living throught movement, healing, and creation",
        }
        return render(request, "taiping/course/list.html", context)

    def post(self, request: HttpRequest, course_id: int | None = None) -> HttpResponse:
        if name := request.GET.get("htmx"):
            return getattr(self, f"htmx_{name.replace("-", "_")}")(request)

        return HttpResponse("", status=405)
