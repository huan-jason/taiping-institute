from typing import Any, cast
from django.db.models import F
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from taiping.models import Course, CourseClass, Registration


class EnrollView(View):

    def course_class_details(self,
        request: HttpRequest,
        course_id: int,
        course_class_id: int,
    ) -> HttpResponse:

        course_class_id = int(request.GET.get("course_class_id") or course_class_id)
        course: Course = get_object_or_404(Course.objects.filter(id=course_id))
        course_class: CourseClass | None = CourseClass.objects.filter(id=course_class_id).first()
        return render(request, "taiping/registration/course_class_details.html", locals())

    def get(self, request: HttpRequest, course_id: int, course_class_id: int = 0) -> HttpResponse:
        if request.GET.get("htmx") == "course-class-details":
            return self.course_class_details(
                request=request,
                course_id=course_id,
                course_class_id=course_class_id,
            )
        course: Course = get_object_or_404(Course.objects.filter(id=course_id))
        dependent_courses: list[dict] = self.get_dependent_courses(request, course)
        met_prerequisites: bool = all(item["met_dependency"] for item in dependent_courses)
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
