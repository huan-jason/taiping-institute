import json
import logging
from typing import Any, cast
from django.core.mail import send_mail
from django.forms import model_to_dict
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views import View

from taiping.models import (
    Config,
    Course,
    Registration,
)


class RegisterView(View):

    def check_prerequisites(self, request: HttpRequest, course_id: int) -> HttpResponse:
        email: str = request.POST["email"]
        course: Course = Course.objects.get(id=course_id)
        prerequisites: list[Course] = course.prerequisites()
        results: list[dict[str, Any]] = []

        for item in prerequisites:
            data: dict[str, Any] = model_to_dict(item)
            data["completed"] = item.met_prerequisites(email)
            results.append(data)

        prerequisites = cast(Any, results)
        check_prerequisites: bool = True
        all_completed: bool = all(item["completed"] for item in prerequisites)
        error_message: str = ("" if all_completed else
            "You have not met all the prerequisites of this course."
        )
        return render(request, "taiping/registration/prerequisites.html", locals())

    def get(self, request: HttpRequest, course_id: int) -> HttpResponse:
        course: Course | None = Course.objects.filter(id=course_id).first()
        prerequisites: list[Course] = course.prerequisites()
        return (
            render(request, "taiping/registration/register.html", locals())
            if course else
            HttpResponse(f"Invalid course ID: {course_id}", status=404)
        )

    def post(self, request: HttpRequest, course_id: int) -> HttpResponse:
        if "check-prerequisites" in request.GET:
            return self.check_prerequisites(request, course_id)

        course: Course = Course.objects.get(id=course_id)
        email: str = request.POST["email"]

        registration: Registration | None = (Registration.objects
            .filter(
                course_id=course_id,
                email=email,
            )
            .first()
        )

        if registration:
            css_classes: str = "text-danger fs-1"
            message: str = f"You have already registered for {course.name} on {registration.created:%d-%b-%Y}."
            return render(request, "taiping/message.html", locals())

        Registration.objects.create(
            course_id=course_id,
            name=request.POST["name"],
            email=email,
            tel=request.POST["tel"],
            comments=request.POST["comments"],
        )

        self.send_notification(request, course)

        css_classes = "fs-1"
        message = (
            f"Thank you for registering for {course.name}.  "
            "We will notify you when the course details are available."
        )
        return render(request, "taiping/message.html", locals())

    def send_notification(self, request: HttpRequest, course: Course) -> None:
        recipient_list: list[str] = list(Config.registration_notification().values_list("value", flat=True))
        message: str = render_to_string("taiping/registration_notification.html", context=locals(), request=request)

        try: send_mail(
            subject=f"Course Registration: {course.name}",
            from_email=None,
            recipient_list=recipient_list,
            message=message,
            fail_silently=False,
        )
        except Exception as e:
            logging.error(f"Send mail error: {e}")

