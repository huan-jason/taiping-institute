from datetime import date
from typing import Any, cast

from django.db.models import QuerySet
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import View

from taiping.models import (
    CourseClass,
    CourseClassStudent,
    Instructor,
)


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

    def get_bar_heights(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        min_amount, max_amount = self.get_chart_min_max_amounts(data)
        total: float = (max_amount - min_amount) or max_amount
        low: float = 0 if min_amount == max_amount else (min_amount - total * 0.1)
        unit_val: float = (100 / total) if total else 0

        for item in data:
            amount: float = item["amount"]
            val: float = max(amount - low, 0)
            item["height"] = f"{int(val * unit_val)}"

        return data

    def get_chart_min_max_amounts(self, data: list[dict[str, Any]]) -> tuple[float, float]:
        amounts: list[float] = [amount for item in data if (amount := item["amount"])] or [0]
        min_amount: float = min(amounts)
        max_amount: float = max(amounts)
        return min_amount, max_amount

    def get_previous_month(self, month: date) -> date:
        month_: int = month.month - 1
        year_: int = month.year

        return month.replace(
            month=month_ or 12,
            year=year_ if month_ else year_ - 1,
        )

    def get_revenues(self, instructor: Instructor, months: int = 6) -> list[dict[str, Any]]:
        month: date = timezone.now().date().replace(day=1)
        revenues: list[dict[str, Any]] = []

        for item in range(months):
            revenues.append({
                "month": month,
                "amount": instructor.get_revenue(month),
                "height": 0,
            })
            month = self.get_previous_month(month)

        return self.get_bar_heights(revenues[::-1])

    def get_ytd_amount(self, instructor: Instructor) -> float:
        month: date = timezone.now().date().replace(day=1)
        year: int = month.year
        amount: float = 0

        while month.year == year:
            amount += instructor.get_revenue(month)
            month = self.get_previous_month(month)

        return amount

    def htmx_overview(self, request: HttpRequest) -> HttpResponse:
        instructor: Instructor | None = getattr(request.user, "instructor", None)
        return render(request, "agojin/instructor/overview.html", locals())

    def htmx_enrolled_students(self, request: HttpRequest) -> HttpResponse:
        instructor: Instructor | None = getattr(request.user, "instructor", None)
        course_class_students: QuerySet[CourseClassStudent] = (CourseClassStudent.objects
            .filter(course_class__instructor=instructor)
            .order_by("-created")
        )
        return render(request, "agojin/instructor/enrolled_students.html", locals())

    def htmx_manage_courses(self, request: HttpRequest) -> HttpResponse:
        instructor: Instructor | None = getattr(request.user, "instructor", None)
        course_classes: QuerySet[CourseClass] = (CourseClass.objects
            .filter(instructor=instructor)
            .order_by("-start_date")
        )
        return render(request, "agojin/instructor/manage_courses.html", locals())

    def htmx_revenue(self, request: HttpRequest) -> HttpResponse:
        instructor: Instructor | None = getattr(request.user, "instructor", None)
        revenues: list[dict[str, Any]] = []

        if instructor:
            revenues = self.get_revenues(instructor)
            ytd_amount: float = self.get_ytd_amount(instructor)

        return render(request, "agojin/instructor/revenue.html", locals())

    def htmx_schedule(self, request: HttpRequest) -> HttpResponse:
        instructor: Instructor | None = getattr(request.user, "instructor", None)
        return render(request, "agojin/instructor/schedule.html", locals())

    def htmx_stats(self, request: HttpRequest) -> HttpResponse:
        instructor: Instructor | None = getattr(request.user, "instructor", None)
        return render(request, "agojin/instructor/stats.html", locals())
