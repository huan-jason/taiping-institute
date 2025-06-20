from typing import Any, cast

from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from taiping.models import Course, CourseClass, Registration


class IndexView(View):

    TABS: dict[str, dict] = {
        "student": {
            "id": "student",
            "label": "Student Info",
            "show": False,
        },
        "instructor": {
            "id": "instructor",
            "label": "Instructor Info",
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

        if "htmx" in request.GET:
            return self.htmx(request)

        user: User = cast(User, request.user)
        is_instructor: bool = hasattr(user,"instructor")
        is_student: bool = hasattr(user,"student")
        tabs: dict[str, dict] = self.TABS
        active_tab: str = ""

        if is_instructor:
            active_tab = "instructor"
            tabs["instructor"]["show"] = True

        if is_student:
            tabs["student"]["show"] = True
            if not is_instructor:
                active_tab = "dashboard"

        return render(request, "taiping/dashboard/index.html", locals())

    def htmx(self, request: HttpRequest) -> HttpResponse:
        htmx: str = f"htmx_{request.GET["htmx"]}"
        return getattr(self, htmx)(request)

    def htmx_courses(self, request: HttpRequest) -> HttpResponse:
        show_create_course_button: bool = True
        courses: QuerySet[Course] = Course.objects.order_by("sort_order", "name")
        return render(request, "taiping/dashboard/courses.html", locals())

    def htmx_instructor(self, request: HttpRequest) -> HttpResponse:
        user: Any = request.user
        course_classes: QuerySet[CourseClass] = CourseClass.objects.filter(instructor=user.instructor)
        return render(request, "taiping/dashboard/instructor.html", locals())

    def htmx_student(self, request: HttpRequest) -> HttpResponse:
        user: Any = request.user
        registrations: QuerySet[Registration] = Registration.objects.filter(student=user.student)
        return render(request, "taiping/dashboard/student.html", locals())
