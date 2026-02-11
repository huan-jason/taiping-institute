from typing import Any, cast

from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from taiping.models import (
    CourseClass,
    Registration,
)
from taiping.utils import get_courses_list_context


class IndexView(View):

    TABS: dict[str, dict] = {
        "instructor": {
            "id": "instructor",
            "label": "Instructor Dashboard",
            "show": False,
        },
        "student": {
            "id": "student",
            "label": "Student Dashboard",
            "show": False,
        },
        "courses": {
            "id": "courses",
            "label": "Courses",
            "show": True,
        },
    }

    def get(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect("course_list")

        if htmx := request.GET.get("htmx"):
            return getattr(self, f"htmx_{request.GET["htmx"]}")(request)

        user: Any = self.get_user(request)
        is_instructor: bool = hasattr(user, "instructor")
        is_student: bool = hasattr(user, "student")
        tabs: dict[str, dict] = self.TABS
        active_tab: str = ""
        show_create_course_button: bool = (request.user.groups
            .filter(name="data_admin")
            .exists()
        )

        if is_instructor:
            active_tab = "instructor"
            tabs["instructor"]["show"] = True

        if is_student:
            tabs["student"]["show"] = True
            if not is_instructor:
                active_tab = (
                    "student"
                    if Registration.objects.filter(student=user.student).exists()
                    else "courses"
                )

        if tab := request.GET.get("tab"):
            active_tab = tab

        request.session["course_filters"] = {  # for htmx calls
            key: request.GET[key]
            for key in request.GET
            if key.startswith("filter_")
        }

        return render(request, "taiping/dashboard/index.html", locals())

    def get_user(self, request: HttpRequest) -> User:
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
