from typing import Any, cast
from django.db.models import F
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from taiping.models import Course, Registration


class EnrollView(View):

    def get(self, request: HttpRequest, course_id: int, course_class_id: int) -> HttpResponse:

        course: Course = get_object_or_404(Course.objects.filter(id=course_id))
        dependent_courses: list[dict] = self.get_dependent_courses(request, course)
        met_prequisites: bool = all(item["met_dependency"] for item in dependent_courses)
        return render(request, "taiping/registration/index.html", locals())

    def get_dependent_courses(self, request: HttpRequest, course: Course) -> list[dict]:
        student_course_ids: set[int] = {
            item.course_class.course_id for item in
            Registration.objects.filter(student=cast(Any, request).user, completed=True)
        }
        dependent_courses: list[dict] = list(course
            .coursedependency_set # type: ignore
            .annotate(dependency_course=F("dependent_course__name"))
            .values()
        )

        for item in dependent_courses:
            item["met_dependency"] = item["dependent_course_id"] in student_course_ids

        return dependent_courses

    def post(self, request: HttpRequest, course_id: int | None = None) -> HttpResponse:
        raise NotImplementedError
