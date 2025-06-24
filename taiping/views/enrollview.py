import logging
from typing import Any, cast

from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views import View

from taiping.constants import UserTypeChoices
from taiping.models import (
    Course,
    CourseClass,
    Instructor,
    Registration,
    Student,
)


class EnrollView(View):

    def course_class_details(self,
        request: HttpRequest,
        course_id: int,
        course_class_id: int,
    ) -> HttpResponse:

        course: Course = get_object_or_404(Course.objects.filter(id=course_id))

        course_class_id = int(request.GET.get("course_class_id") or course_class_id)
        course_class: CourseClass | None = (
            CourseClass.objects.filter(id=course_class_id).first()
            if course_class_id else
            CourseClass.objects.filter(course_id=course_id).order_by("start_date").first()
        )
        enrolled_class_ids: set[int] = set(Registration.objects
            .filter(
                student__user=cast(Any, request.user),
                course_class__course_id=course_id,
            )
            .values_list("course_class_id", flat=True)
        )
        return render(request, "taiping/enrollment/course_class_details.html", locals())

    def get(self, request: HttpRequest, course_id: int, course_class_id: int = 0, enrolled: bool = False) -> HttpResponse:
        if not hasattr(request.user, "student"):
            return redirect("create_account")

        if request.GET.get("htmx") == "course-class-details":
            return self.course_class_details(
                request=request,
                course_id=course_id,
                course_class_id=course_class_id,
            )

        if enrolled:
            return self.enrolled(request, course_class_id)

        course: Course = get_object_or_404(Course.objects.filter(id=course_id))
        dependent_courses: list[dict] = self.get_dependent_courses(request, course)
        met_prerequisites: bool = all(item["met_dependency"] for item in dependent_courses)
        show_back_button: bool = True
        return render(request, "taiping/enrollment/index.html", locals())

    def enrolled(self, request: HttpRequest, course_class_id: int)-> HttpResponse:
        course_class: CourseClass = (CourseClass.objects
            .select_related("course")
            .get(id=course_class_id)
        )
        return render(request, "taiping/enrollment/enrolled.html", locals())


    def get_dependent_courses(self, request: HttpRequest, course: Course) -> list[dict]:
        student_course_ids: set[int] = {
            item.course_class.course_id for item in
            Registration.objects.filter(student=cast(Any, request).user.student, completed=True)
        }
        dependent_courses: list[dict] = list(course
            .coursedependency_set # type: ignore
            .annotate(dependency_course=F("dependent_course__name"))
            .values()
        )

        for item in dependent_courses:
            item["met_dependency"] = item["dependent_course_id"] in student_course_ids

        return dependent_courses

    def post(self, request: HttpRequest, course_id: int | None = None, **kwargs: Any) -> HttpResponse:
        course_class: CourseClass = (CourseClass.objects
            .select_related("course")
            .get(id=int(request.POST["course_class_id"]))
        )

        with transaction.atomic():
            try:
                Registration.objects.create(
                    course_class=course_class,
                    student=cast(Any, request.user).student,
                )
                self.send_emails(request, course_class)
            except Exception as exc:
                logging.error(exc)
                if "debug" in request.GET: raise
                return HttpResponse(
                    f"<div>A system error occurred</div>"
                    f"<div style='margin-top:2em'>{exc}</div>"
                )

        return redirect(
            "enrolled",
            course_id=course_id,
            course_class_id=int(request.POST["course_class_id"]),
        )

    def send_email(self, request: HttpRequest, course_class: CourseClass, email_type: UserTypeChoices) -> None:
        student: Student = cast(Any, request.user).student
        instructor: Instructor = course_class.get_instructor
        message: str = render_to_string(
            request=request,
            template_name=f"taiping/enrollment/enrolled_email_{email_type}.txt",
            context=locals(),
        )
        html_message: str = render_to_string(
            request=request,
            template_name=f"taiping/enrollment/enrolled_email_{email_type}.html",
            context=locals(),
        )
        course_name: str = f"{course_class.course.name} ({course_class.course.chinese_name})"
        send_mail(
            subject=f"Agojin Course Enrollment: {course_name}",
            from_email=None,
            recipient_list=[cast(Any, request.user).email],
            message=message,
            html_message=html_message,
            fail_silently=False,
        )

    def send_emails(self, request: HttpRequest, course_class: CourseClass) -> None:
        self.send_email(request=request, course_class=course_class, email_type=UserTypeChoices.STUDENT)
        self.send_email(request=request, course_class=course_class, email_type=UserTypeChoices.INSTRUCTOR)
