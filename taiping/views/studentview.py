from typing import cast

from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View


class StudentView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        if htmx := request.GET.get("htmx"):
            return getattr(self, f"htmx_{htmx}")(request)

        user: User | None = self.get_user(request)
        is_instructor: bool = hasattr(user, "instructor")
        is_student: bool = hasattr(user, "student")
        current_tab: str = "student"

        return render(request, "agojin/student/index.html", locals())

    def get_user(self, request: HttpRequest) -> User | None:
        if not request.user.is_authenticated: return None
        user: User = cast(User, request.user)
        if not user.is_superuser: return user
        if not (username := request.GET.get("u")): return user
        if not (user_ := User.objects.filter(username=username).first()):
            raise Exception(f"Invalid username: {username}")
        return user_
