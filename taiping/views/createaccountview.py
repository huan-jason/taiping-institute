from datetime import datetime
from typing import Any, Literal, TypeAlias, cast

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views import View

from taiping.constants import GenderChoices
from taiping.models import EmailVerification, Student


UserType: TypeAlias = Literal["student", "instructor"]


class CreateAccountView(View):

    DATE_FIELDS: list[str] = [
        "date_of_birth",
    ]

    FILE_FIELDS: list[str] = [
        "profile_photo",
    ]

    INT_FIELDS: list[str] = [
        "experience_years",
    ]

    TEXT_FIELDS: list[str] = [
        "alternative_name",
        "gender",
        "phone",
        "styles_trained",
        "medical_conditions",
        "preferred_languages",
        "emergency_contact_name",
        "emergency_contact_phone",
    ]

    def account_created(self, request: HttpRequest) -> HttpResponse:
        student: Student = Student.objects.get(id=request.GET["student"])
        return render(request, "taiping/create_account/created.html", locals())


    def create_instructor(self, request: HttpRequest) -> HttpResponse:
        raise NotImplementedError

    def create_student(self, request: HttpRequest) -> HttpResponse:
        user: User = self.create_user(request)
        data: dict = {
            "user": user,
        }
        data |= {
            key: request.POST[key]
            for key in self.TEXT_FIELDS
        }
        data |= {
            key: int(request.POST[key])
            for key in self.INT_FIELDS
        }
        data |= {
            key: datetime.strptime(request.POST[key], "%Y-%m-%d")
            for key in self.DATE_FIELDS
        }
        data |= {
            name: ContentFile(
                cast(Any, upload).file.read(),
                name=f"student_{cast(Any, user).id}_{cast(Any, upload)._name}",
            )
            for name, upload in request.FILES.items()
        }

        student: Student = Student.objects.create(**data)
        self.send_email(request, student)
        return redirect(f"/create-account/created/?student={cast(Any, student).id}")

    def create_user(self, request: HttpRequest) -> User:
        email: str = request.POST["email"]
        return User.objects.create(
            username=email.lower(),
            first_name=request.POST["first_name"],
            last_name=request.POST["last_name"],
            email=email,
        )

    def get(self, request: HttpRequest, user_type: UserType="student", created: bool = False) -> HttpResponse:
        if created:
            return self.account_created(request)

        gender_options: list[tuple[str, str]] = list(cast(Any, GenderChoices.choices))
        return render(request, f"taiping/create_account/{ user_type }.html", locals())

    def get_email_message(self, request: HttpRequest, student: Student, message_type: str) -> str:
        return render_to_string(
            request=request,
            template_name=f"taiping/create_account/created_email.{message_type}",
            context=locals(),
        )

    def get_verification_code(self, request: HttpRequest) -> HttpResponse:
        email: str = request.POST["email"].strip().lower()
        user_exists: bool = User.objects.filter(username=email).exists()
        if user_exists:
            return render(request, "taiping/create_account/user_exists.html", locals())

        verification_code: str = EmailVerification.gen_code()
        EmailVerification.objects.update_or_create(
            email=email,
            defaults={ "code": verification_code },
        )
        send_mail(
            subject="Agojin Email Verification",
            message=f"Your Agojin email verification code is {verification_code}.",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )
        return render(request, "taiping/create_account/verification_code.html", locals())

    def post(self, request: HttpRequest, user_type: UserType="student") -> HttpResponse:
        htmx: str = request.GET.get("htmx", "")

        if htmx == "get-verification-code":
            return self.get_verification_code(request)
        if htmx == "verify-code":
            return self.verify_code(request)

        with transaction.atomic():
            return (
                self.create_student(request)
                if user_type == "student" else
                self.create_instructor(request)
            )

    def send_email(self, request: HttpRequest, student: Student) -> None:
        send_mail(
            subject="Welcome to Agojin",
            from_email=None,
            recipient_list=[student.user.email],
            fail_silently=False,
            message=self.get_email_message(request=request, student=student, message_type="txt"),
            html_message=self.get_email_message(request=request, student=student, message_type="html"),
        )

    def verify_code(self, request: HttpRequest) -> HttpResponse:
        verification_code: str = request.POST["email_verification_code"]
        verified: EmailVerification | None = (EmailVerification.objects
            .filter(
                email=request.POST["email"].lower(),
                code=verification_code,
            ).first()
        )
        return render(request, "taiping/create_account/verify_code.html", locals())

