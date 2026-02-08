from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from taiping.models import Course, Facility, Instructor
from .classschedulemixin import ClassScheduleMixin


class CourseView(ClassScheduleMixin, View):

    def get(self, request: HttpRequest, course_id: int | None = None) -> HttpResponse:

        if name := request.GET.get("htmx"):
            return getattr(self, f"htmx_{name.replace("-", "_")}")(request)

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
        show_create_course_button: bool = (request.user.groups
            .filter(name="data_admin")
            .exists()
        )
        filters: dict = {
            key: int(val) if val and key != "filter_month" else val
            for key, val in (request.session.get("course_filters") or {}).items()
        }
        has_filters: bool = any(filters.values())
        courses: QuerySet[Course] = Course.objects.order_by("sort_order", "name")
        course_groups: QuerySet[Course] = (Course.objects
            .select_related("course_group")
            .distinct("course_group__name")
            .order_by("course_group__name")
        )
        facilities: QuerySet[Facility] = Facility.objects.order_by("name")
        instructors: QuerySet[Instructor] = Instructor.objects.order_by("user__first_name", "user__last_name")
        return render(request, "taiping/course/list.html", locals())

    def post(self, request: HttpRequest, course_id: int | None = None) -> HttpResponse:
        if name := request.GET.get("htmx"):
            return getattr(self, f"htmx_{name.replace("-", "_")}")(request)

        return HttpResponse("", status=405)
