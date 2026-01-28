from datetime import date, datetime
from typing import Any, Literal, TypeAlias, cast

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views import View

from taiping.constants import GenderChoices, ComplianceTypeChoices
from taiping.models import (
    AppData,
    Compliance,
    EmailVerification,
    Student,
    Instructor,
)


UserType: TypeAlias = Literal["student", "instructor"]


class CreateAccountView(View):

    STUDENT_FIELDS: dict[str, list[str]] = {
        "date": [
            "date_of_birth",
        ],
        "int": [
            "experience_years",
        ],
        "text": [
            "alternative_name",
            "gender",
            "phone",
            "styles_trained",
            "medical_conditions",
            "preferred_languages",
            "emergency_contact_name",
            "emergency_contact_phone",
        ],
    }

    INSTRUCTOR_FIELDS: dict[str, list[str]] = {
        "text": [
            "bio",
            "certifications",
        ],
    }

    def account_created(self, request: HttpRequest) -> HttpResponse:
        return render(request, "taiping/create_account/created.html", locals())

    def archive_compliance(self,
        compliance_type: ComplianceTypeChoices,
        student: Student | None = None,
        instructor: Instructor | None = None,
    ) -> None:

        app_data: AppData = AppData.objects.get(name=compliance_type.replace(" ", "_"))
        Compliance.objects.create(
            student=student,
            instructor=instructor,
            compliance_type=compliance_type,
            data=app_data.data
        )

    def check_code(self, request: HttpRequest) -> EmailVerification | None:
        verification_code: str = request.POST["email_verification_code"]
        return (EmailVerification.objects
            .filter(
                email=request.POST["email"].lower(),
                code=verification_code,
            ).first()
        )

    def create_instructor(self, request: HttpRequest) -> HttpResponse:
        user: User = self.create_user(request)
        data: dict = {
            "user": user,
            "date_joined": date.today(),
        }
        data |= {
            key: request.POST[key]
            for key in self.INSTRUCTOR_FIELDS["text"]
        }
        data |= {
            name: ContentFile(
                cast(Any, upload).file.read(),
                name=f"student_{cast(Any, user).id}_{cast(Any, upload)._name}",
            )
            for name, upload in request.FILES.items()
        }

        instructor: Instructor = Instructor.objects.create(**data)
        self.send_email(request, instructor.user)

        self.archive_compliance(
            instructor=instructor,
            compliance_type=ComplianceTypeChoices.INSTRUCTOR_TERMS_AND_CONDITIONS,
        )

        return redirect(f"/create-account/created/?instructor={cast(Any, instructor).id}")

    def create_student(self, request: HttpRequest) -> HttpResponse:
        is_instructor: bool = hasattr(request.user, "instructor")
        user: User = cast(Any, request.user) if is_instructor else self.create_user(request)
        data: dict = {
            "user": user,
        }
        data |= {
            key: request.POST[key]
            for key in self.STUDENT_FIELDS["text"]
        }
        data |= {
            key: int(request.POST[key])
            for key in self.STUDENT_FIELDS["int"]
        }
        data |= {
            key: datetime.strptime(request.POST[key], "%Y-%m-%d")
            for key in self.STUDENT_FIELDS["date"]
        }

        if is_instructor:
            data |= {
                "photo": cast(Any, request.user).instructor.photo,
            }
        else:
            data |= {
                name: ContentFile(
                    cast(Any, upload).file.read(),
                    name=f"student_{cast(Any, user).id}_{cast(Any, upload)._name}",
                )
                for name, upload in request.FILES.items()
            }

        student: Student = Student.objects.create(**data)

        if not hasattr(request.user, "instructor"):
            self.send_email(request, student.user)

        self.archive_compliance(
            student=student,
            compliance_type=ComplianceTypeChoices.TERMS_AND_CONDITIONS,
        )
        self.archive_compliance(
            student=student,
            compliance_type=ComplianceTypeChoices.INDEMNITY_WAIVER,
        )

        return redirect(f"/create-account/created/?student={cast(Any, student).id}")

    def create_user(self, request: HttpRequest) -> User:
        email: str = request.POST["email"]
        return User.objects.create(
            username=email.lower(),
            first_name=request.POST["first_name"],
            last_name=request.POST["last_name"],
            email=email,
        )

    def get(self, request: HttpRequest, user_type: UserType = "student", created: bool = False) -> HttpResponse:
        if created:
            return self.account_created(request)

        user: Any = request.user

        if user_type == "student" and hasattr(user, "student"):
            return HttpResponse("You have already registered as a student.")

        elif user_type == "instructor" and hasattr(user, "instructor"):
            return HttpResponse("You have already registered as an instructor.")

        app_data: dict = self.get_app_data()
        terms_and_conditions_key: str = (
            ComplianceTypeChoices.INSTRUCTOR_TERMS_AND_CONDITIONS.name.lower()
            if user_type == "instructor" else
            ComplianceTypeChoices.TERMS_AND_CONDITIONS.name.lower()
        )
        terms_and_conditions: str = app_data[terms_and_conditions_key].data

        gender_options: list[tuple[str, str]] = list(cast(Any, GenderChoices.choices))
        return render(request, f"taiping/create_account/{user_type}.html", locals())

    def get_app_data(self) -> dict:
        names: list[str] = [item.lower() for item in ComplianceTypeChoices._member_names_]
        return (AppData.objects
            .filter(name__in=names)
            .in_bulk(field_name="name")
        )

    def get_email_message(self, request: HttpRequest, user: User, message_type: str) -> str:
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
            defaults={"code": verification_code},
        )
        send_mail(
            subject="Agojin Email Verification",
            message=f"Your Agojin email verification code is {verification_code}.",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )
        return render(request, "taiping/create_account/verification_code.html", locals())

    def post(self, request: HttpRequest, user_type: UserType = "student") -> HttpResponse:
        htmx: str = request.GET.get("htmx", "")

        if htmx == "get-verification-code":
            return self.get_verification_code(request)
        if htmx == "verify-code":
            return self.verify_code(request)

        if not hasattr(request.user, "instructor") and not self.check_code(request):
            return HttpResponse("", status=403)

        with transaction.atomic():
            return (
                self.create_student(request)
                if user_type == "student" else
                self.create_instructor(request)
            )

    def send_email(self, request: HttpRequest, user: User) -> None:
        send_mail(
            subject="Welcome to Agojin",
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
            message=self.get_email_message(request=request, user=user, message_type="txt"),
            html_message=self.get_email_message(request=request, user=user, message_type="html"),
        )

    def verify_code(self, request: HttpRequest) -> HttpResponse:
        verified: EmailVerification | None = self.check_code(request)
        return render(request, "taiping/create_account/verify_code.html", locals())
