from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from taiping.models import Course


class CoursesView(View):

    def get(self, request: HttpRequest, course_id: int | None = None) -> HttpResponse:

        if not course_id:
            courses: QuerySet[Course] = Course.objects.order_by("sort_order", "name")
            return render(request, "taiping/courses.html", locals())

        raise NotImplementedError
