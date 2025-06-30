from datetime import datetime, date
from typing import Any, cast

from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View

from taiping.constants import CourseStatusChoices
from taiping.models import (
    Course,
    CourseClass,
    CourseGroup,
    Facility,
    Instructor,
)
from .classschedulemixin import ClassScheduleMixin


class CourseEditView(ClassScheduleMixin, View):

    COURSE_FIELDS: dict[str, list[str]] = {
        "text": [
            "name",
            "chinese_name",
            "description",
            "short_description",
        ],
        "int": [
            "instructor_id",
            "facility_id",
            "course_fee",
            "min_students",
            "max_students",
        ],
        "optional_int": [
            "course_group_id",
        ]
    }

    COURSE_CLASS_FIELDS: dict[str, list[str]] = {
        "text": [
            "status",
            "notes",
        ],
        "date": [
            "start_date",
            "end_date",
        ],
        "int": [
            "course_id",
            "facility_id",
            "instructor_id",
            "course_fee",
            "max_students",
            "min_students",
        ],
        "checkbox": [
            "auto_start",
        ],
    }

    def check_field_name(self, request: HttpRequest) -> HttpResponse:
        field: str = "name"
        value: str = request.GET[field].strip()
        if not value: return HttpResponse("")

        error: bool = Course.objects.filter(name__iexact=value).exists()
        error_message: str = f"Course name {value} already exists"

        return render(request, "taiping/course/check_field.html", locals())

    def check_field_chinese_name(self, request: HttpRequest) -> HttpResponse:
        field: str = "chinese_name"
        value: str = request.GET[field].strip()
        if not value: return HttpResponse("")

        error: bool = Course.objects.filter(chinese_name=value).exists()
        error_message: str = f"Course name {value} already exists"

        return render(request, "taiping/course/check_field.html", locals())

    def delete_course_class(self, request: HttpRequest) -> HttpResponse:
        course_class_id: str = request.POST["course_class_id"]
        CourseClass.objects.filter(id=course_class_id).delete()

        course_id: int = int(request.POST["course_id"])
        return redirect("course_edit", course_id=course_id)

    def get(self, request: HttpRequest, course_id: int | None = None) -> HttpResponse:
        if (action := request.GET.get("htmx")):
            action = action.replace("-", "_")
            return getattr(self, f"htmx_{action}")(request)

        today: date = timezone.now().date()
        course: Course | None = Course.objects.filter(id=course_id or 0).first()
        course_classes: QuerySet[CourseClass] | list = (course
            .courseclass_set # type: ignore
            .order_by("start_date", "end_date")
        ) if course else []

        edit_mode: bool = True
        course_groups: QuerySet[CourseGroup] = CourseGroup.objects.order_by("name")
        facilities: QuerySet[Facility] = Facility.objects.order_by("name")
        instructors: QuerySet[Instructor] = Instructor.objects.order_by("user__first_name", "user__last_name")
        return render(request, "taiping/course/edit.html", locals())

    def htmx_check_field(self, request: HttpRequest) -> HttpResponse:
        field: str = request.GET["field"]
        return getattr(self, f"check_field_{field}")(request)

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
        course_status_choices: list[tuple[str, str]] = list(cast(Any, CourseStatusChoices.choices))
        return render(request, "taiping/course/modal_course_class/modal_content.html", locals())

    def post(self, request: HttpRequest, course_id: int | None = None) -> HttpResponse:
        if (action := request.GET.get("htmx")):
            action = action.replace("-", "_")
            return getattr(self, f"htmx_{action}")(request)

        if "delete" in request.POST:
            return self.delete_course_class(request)

        if "save_modal_course_class" in request.GET:
            return self.save_course_class(request)

        with transaction.atomic():
            course: Course = Course() if not course_id else Course.objects.get(id=course_id)
            data: dict = {}
            data |= {
                name: request.POST[name]
                for name in self.COURSE_FIELDS["text"]
            }
            data |= {
                name: int(request.POST[name])
                for name in self.COURSE_FIELDS["int"]
            }
            data |= {
                name: int(value)
                for name in self.COURSE_FIELDS["optional_int"]
                if (value := request.POST[name])
            }

            for key, val in data.items():
                setattr(course, key, val)

            course.save()  # obtain course id

            for name, upload in request.FILES.items():
                content_file: ContentFile = ContentFile(
                    cast(Any, upload).file.read(),
                    name=f"course__{cast(Any, course).id}__{cast(Any, upload)._name}",
                )
                setattr(course, name, content_file)

            course.save()
            return (
                redirect("course", course_id=(cast(Any, course).id))
                if course_id else
                redirect("course_list")
            )

    def save_course_class(self, request: HttpRequest) -> HttpResponse:
        course_class_id: str = request.POST["course_class_id"]
        course_id: int = int(request.POST["course_id"])
        course_class: CourseClass = (
            CourseClass.objects.get(id=int(course_class_id))
            if course_class_id else
            CourseClass()
        )
        data: dict = {}
        data |= {
            field: request.POST[field]
            for field in self.COURSE_CLASS_FIELDS["text"]
        }
        data |= {
            field: int(request.POST[field])
            for field in self.COURSE_CLASS_FIELDS["int"]
        }
        data |= {
            field: datetime.strptime(request.POST[field], "%Y-%m-%d").date()
            for field in self.COURSE_CLASS_FIELDS["date"]
        }
        data |= {
            field: field in request.POST
            for field in self.COURSE_CLASS_FIELDS["checkbox"]
        }

        for key, val in data.items():
            setattr(course_class, key, val)

        course_class.save()
        return redirect("course_edit", course_id=course_id)
