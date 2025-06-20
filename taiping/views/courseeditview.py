from typing import Any, cast

from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from taiping.models import (
    Course,
    CourseClass,
    CourseGroup,
    Facility,
    Instructor,
)


class CourseEditView(View):

    COURSE_FIELDS: dict[str, list[str]] = {
        "text": [
            "name",
            "chinese_name",
            "description",
            "short_description",
        ],
        "int": [
            "course_group_id",
            "instructor_id",
            "facility_id",
            "course_fee",
            "min_students",
            "max_students",
        ],
    }

    def get(self, request: HttpRequest, course_id: int | None = None) -> HttpResponse:
        if (action := request.GET.get("htmx")):
            action = action.replace("-", "_")
            return getattr(self, f"htmx_{action}")(request)

        course: Course | None = Course.objects.filter(id=course_id or 0).first()
        course_groups: QuerySet[CourseGroup] = CourseGroup.objects.order_by("name")
        facilities: QuerySet[Facility] = Facility.objects.order_by("name")
        instructors: QuerySet[Instructor] = Instructor.objects.order_by("user__first_name", "user__last_name")
        return render(request, "taiping/course/edit.html", locals())

    def htmx_modal_course_class(self, request: HttpRequest) -> HttpResponse:
        course_class_id : str = request.GET.get("id", "")
        action: str = "Edit" if course_class_id else "Add"
        course: Course = Course.objects.get(id=request.GET["course"])
        course_class: CourseClass = (
            CourseClass.objects.select_related("course").get(id=int(course_class_id))
            if course_class_id else
            CourseClass()
        )
        facilities: QuerySet[Facility] = Facility.objects.order_by("name")
        instructors: QuerySet[Instructor] = Instructor.objects.order_by("user__first_name", "user__last_name")
        return render(request, "taiping/course/modal_course_class/modal_content.html", locals())

    def post(self, request: HttpRequest, course_id: int | None = None) -> HttpResponse:

        if "save_modal_course_class" in request.GET:
            return self.save_modal_course_class(request)

        with transaction.atomic():
            course: Course = Course() if not course_id else Course.objects.get(id=course_id)
            data: dict = {
                name: request.POST[name]
                for name in request.POST.keys()
            }
            data |= {
                name: request.POST[name]
                for name in self.COURSE_FIELDS["text"]
            }
            data |= {
                name: int(request.POST[name])
                for name in self.COURSE_FIELDS["int"]
            }

            for key, val in data.items():
                setattr(course, key, val)

            course.save()

            for name, upload in request.FILES.items():
                content_file: ContentFile = ContentFile(
                    cast(Any, upload).file.read(),
                    name=f"course__{cast(Any, course).id}__{cast(Any, upload)._name}",
                )
                setattr(course, name, content_file)

            course.save()
            return redirect("course_list")

    def save_modal_course_class(self, request: HttpRequest) -> HttpResponse:
        raise NotImplementedError
