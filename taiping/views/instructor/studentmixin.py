from django.db.models import QuerySet
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render

from taiping.models import Instructor, CourseClassStudent


class StudentMixin:

    def student__export(self, request: HttpRequest) -> HttpResponse:
        instructor: Instructor | None = getattr(request.user, "instructor", None)
        if not instructor: return HttpResponse("", status=204)

        data: QuerySet[CourseClassStudent] = (CourseClassStudent.objects
            .filter(course_class__instructor=instructor)
            .order_by("-created")
        )
        response: HttpResponse = render(request, "agojin/instructor/students.csv", locals())
        response["content-disposition"] = "attachment;filename=students.csv"
        return response
