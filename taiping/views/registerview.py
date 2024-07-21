from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from taiping.models import Course


class RegisterView(View):

    def get(self, request: HttpRequest, course_id: int | None = None) -> HttpResponse:

        if not course_id:
            courses: QuerySet[Course] = Course.objects.order_by("sort_order", "name")
            return render(request, "taiping/registration/courses_list.html", locals())

        course: Course | None = Course.objects.filter(id=course_id).first()
        return (
            render(request, "taiping/registration/register.html", locals())
            if course else
            HttpResponse(f"Invalid course ID: {course_id}", status=400)
        )


    def post(self, request: HttpRequest, course_id: int | None = None) -> HttpResponse:
        raise NotImplementedError
