from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from taiping.models import Course


class CourseView(View):

    def get(self, request: HttpRequest, course_id: int | None = None) -> HttpResponse:

        if course_id:
             return self.get_course_detail(request, course_id=course_id)

        return self.get_courses_list(request)

    def get_course_detail(self, request: HttpRequest, course_id: int) -> HttpResponse:
        course: Course | None = Course.objects.filter(id=course_id).first()
        return (
            render(request, "taiping/course/detail.html", locals())
            if course else
            HttpResponse(f"Invalid course ID: {course_id}", status=400)
        )

    def get_courses_list(self, request: HttpRequest) -> HttpResponse:
            courses: QuerySet[Course] = Course.objects.order_by("sort_order", "name")
            return render(request, "taiping/course/list.html", locals())
