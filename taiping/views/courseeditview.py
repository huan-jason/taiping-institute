from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from taiping.models import Course, CourseGroup, Facility, Instructor


class CourseEditView(View):

    def get(self, request: HttpRequest, course_id: int | None = None) -> HttpResponse:
        course: Course | None = Course.objects.filter(id=course_id or 0).first()
        course_groups: QuerySet[CourseGroup] = CourseGroup.objects.order_by("name")
        facilities: QuerySet[Facility] = Facility.objects.order_by("name")
        instructors: QuerySet[Instructor] = Instructor.objects.order_by("user__first_name", "user__last_name")
        return render(request, "taiping/course/edit.html", locals())
