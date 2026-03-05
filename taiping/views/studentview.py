import operator
from typing import Any, Iterable, cast

from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from taiping.models import (
    CourseClass,
    CourseClassSchedule,
    CourseClassStudent,
    Student,
)


class StudentView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        if htmx := request.GET.get("htmx"):
            return getattr(self, f"htmx_{htmx.replace('-', '_')}")(request)

        user: User = cast(Any, request.user)
        student: Student | None = getattr(request.user, "student", None)
        name: str = user.get_full_name()
        name_alt: str = student.alternative_name if student else ""  # type: ignore
        background_char: str = "学"
        current_tab: str = "student"
        title: str = "<em>Student</em> Dashboard"
        subtitle: str = (
            f"{name}" +
            (f"&nbsp;/&nbsp; {name_alt}" if name_alt else "")
        )
        return render(request, "agojin/student/index.html", locals())

    def htmx_enrolled_courses(self, request: HttpRequest) -> HttpResponse:
        user: Any = request.user
        show_action: bool = request.GET.get("a") == "1"
        student_courses: QuerySet[CourseClassStudent] = (CourseClassStudent.objects
            .filter(student__user=user)
            .order_by("-course_class__start_date")
        )
        if (count := request.GET.get("c")):
            student_courses = student_courses[:int(count)]

        return render(request, "agojin/student/enrolled_courses.html", locals())

    def htmx_overview(self, request: HttpRequest) -> HttpResponse:
        return render(request, "agojin/student/overview.html", locals())

    def htmx_progress(self, request: HttpRequest) -> HttpResponse:
        return render(request, "agojin/student/progress.html", locals())

    def htmx_upcoming_classes(self, request: HttpRequest) -> HttpResponse:
        user: Any = request.user
        show_action: bool = request.GET.get("a") == "1"
        course_class_ids: list[int] = list(CourseClassStudent.objects
            .filter(student__user=user)
            .values_list("course_class_id", flat=True)
        )
        upcoming_classes_unsorted: Iterable[CourseClassSchedule] = (
            upcoming_class
            for item in CourseClass.objects.filter(id__in=course_class_ids)
            if (upcoming_class := item.upcoming_class)
        )
        upcoming_classes: list[CourseClassSchedule] = sorted(
            upcoming_classes_unsorted,
            key=operator.attrgetter("class_date")
        )
        if (count := request.GET.get("c")):
            upcoming_classes = upcoming_classes[:int(count)]

        return render(request, "agojin/student/upcoming_classes.html", locals())
