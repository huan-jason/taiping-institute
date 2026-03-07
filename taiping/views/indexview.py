from typing import Any, cast

from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from taiping.constants import CourseStatusChoices
from taiping.models import (
    CourseClass,
    Registration,
)
from taiping.utils import get_courses_list_context


class IndexView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        if htmx := request.GET.get("htmx"):
            return getattr(self, f"htmx_{htmx}")(request)

        context: dict[str, Any] = (
            get_courses_list_context(
                request,
                use_session_filters=True,
                status=CourseStatusChoices.PUBLISHED,
            )
            | dict(
                current_tab="courses",
            )
        )
        return render(request, "agojin/courses/index.html", context)

    def get_user(self, request: HttpRequest) -> User | None:
        if not request.user.is_authenticated: return None
        user: User = cast(User, request.user)
        if not user.is_superuser: return user
        if not (username := request.GET.get("u")): return user
        if not (user_ := User.objects.filter(username=username).first()):
            raise Exception(f"Invalid username: {username}")
        return user_

    def htmx_courses(self, request: HttpRequest) -> HttpResponse:
        context: dict[str, Any] = get_courses_list_context(request, use_session_filters=True)
        return render(request, "taiping/dashboard/courses.html", context)

    def htmx_instructor(self, request: HttpRequest) -> HttpResponse:
        user: Any = self.get_user(request)
        course_classes: QuerySet[CourseClass] = (CourseClass.objects
            .filter(instructor=user.instructor)
            .order_by("start_date", "end_date")
        )
        return render(request, "taiping/dashboard/instructor.html", locals())

    def htmx_student(self, request: HttpRequest) -> HttpResponse:
        user: Any = self.get_user(request)
        registrations: QuerySet[Registration] = (Registration.objects
            .filter(student=user.student)
            .order_by("course_class__start_date", "course_class__end_date")
        )
        return render(request, "taiping/dashboard/student.html", locals())
