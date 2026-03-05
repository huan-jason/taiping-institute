from typing import cast

from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from taiping.models import Student


class StudentView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        if htmx := request.GET.get("htmx"):
            return getattr(self, f"htmx_{htmx.replace('-', '_')}")(request)

        user: User | None = self.get_user(request)
        student: Student | None = getattr(request.user, "student", None)
        name: str = user.get_full_name() if user else ""
        name_alt: str = student.alternative_name if student else ""  # type: ignore
        background_char: str = "学"
        current_tab: str = "student"
        title: str = "<em>Student</em> Dashboard"
        subtitle: str = (
            f"{name}" +
            f"&nbsp;/&nbsp; {name_alt}" if name_alt else ""
        )
        return render(request, "agojin/student/index.html", locals())

    def get_user(self, request: HttpRequest) -> User | None:
        if not request.user.is_authenticated: return None
        user: User = cast(User, request.user)
        if not user.is_superuser: return user
        if not (username := request.GET.get("u")): return user
        if not (user_ := User.objects.filter(username=username).first()):
            raise Exception(f"Invalid username: {username}")
        return user_

    def htmx_enrolled_courses(self, request: HttpRequest) -> HttpResponse:
        show_action: bool = request.GET.get("a") == "1"
        return render(request, "agojin/student/enrolled_courses.html", locals())

    def htmx_overview(self, request: HttpRequest) -> HttpResponse:
        return render(request, "agojin/student/overview.html", locals())

    def htmx_progress(self, request: HttpRequest) -> HttpResponse:
        return render(request, "agojin/student/progress.html", locals())

    def htmx_upcoming_classes(self, request: HttpRequest) -> HttpResponse:
        show_action: bool = request.GET.get("a") == "1"
        return render(request, "agojin/student/upcoming_classes.html", locals())
