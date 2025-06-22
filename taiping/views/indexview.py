from datetime import datetime
from typing import Any

from django.db.models import QuerySet, Q, OuterRef, Exists
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from taiping.constants import CourseStatusChoices
from taiping.models import (
    Course,
    CourseClass,
    Facility,
    Instructor,
    Registration,
)


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

        if "htmx" in request.GET:
            return self.htmx(request)

        user: Any = request.user
        is_instructor: bool = hasattr(user,"instructor")
        is_student: bool = hasattr(user,"student")
        tabs: dict[str, dict] = self.TABS
        active_tab: str = ""
        show_create_course_button: bool = True

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

        request.session["course_filters"] = {
            key: request.GET[key]
            for key in request.GET
            if key.startswith("filter_")
        }

        return render(request, "taiping/dashboard/index.html", locals())

    def get_courses_queryset(self, request: HttpRequest) -> QuerySet[Course]:
        queryset: QuerySet[Course] = Course.objects.order_by("sort_order", "name")
        filters: dict = request.session.get("course_filters") or {}

        if (instructor := filters.get("filter_instructor")):
            queryset = queryset.filter(instructor_id=int(instructor))

        if (facility := filters.get("filter_facility")):
            queryset = queryset.filter(facility_id=int(facility))

        if (course_group := filters.get("filter_course_group")):
            queryset = queryset.filter(course_group_id=int(course_group))

        if (filter_month := filters.get("filter_month")):
            filter_datetime: datetime = datetime.strptime(filter_month, "%Y-%m")
            year: int = filter_datetime.year
            month: int = filter_datetime.month

            q_start_date: Q = Q(start_date__year=year, start_date__month= month)
            q_end_date: Q = Q(end_date__year=year, end_date__month= month)

            subquery: QuerySet[CourseClass] = CourseClass.objects.filter(
                q_start_date | q_end_date,
                course=OuterRef('id'),
                status=CourseStatusChoices.PUBLISHED,
            )
            queryset = queryset.filter(Exists(subquery))

        return queryset

    def htmx(self, request: HttpRequest) -> HttpResponse:
        htmx: str = f"htmx_{request.GET["htmx"]}"
        return getattr(self, htmx)(request)

    def htmx_courses(self, request: HttpRequest) -> HttpResponse:
        show_filters: bool = True
        filters: dict = {
            key: int(val) if val and key != "filter_month" else val
            for key, val in (request.session.get("course_filters") or {}).items()
        }
        has_filters: bool = any(filters.values())
        courses: QuerySet[Course] = self.get_courses_queryset(request)
        course_groups: QuerySet[Course] = Course.objects.select_related("course_group").distinct("course_group")
        facilities: QuerySet[Facility] = Facility.objects.order_by("name")
        instructors: QuerySet[Instructor] = Instructor.objects.order_by("user__first_name", "user__last_name")
        return render(request, "taiping/dashboard/courses.html", locals())

    def htmx_instructor(self, request: HttpRequest) -> HttpResponse:
        user: Any = request.user
        course_classes: QuerySet[CourseClass] = (CourseClass.objects
            .filter(instructor=user.instructor)
            .order_by("start_date", "end_date")
        )
        return render(request, "taiping/dashboard/instructor.html", locals())

    def htmx_student(self, request: HttpRequest) -> HttpResponse:
        user: Any = request.user
        registrations: QuerySet[Registration] = (Registration.objects
            .filter(student=user.student)
            .order_by("course_class__start_date", "course_class__end_date")
        )
        return render(request, "taiping/dashboard/student.html", locals())
