from typing import Any, Literal, TypeAlias, cast

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View
from django.core.mail import send_mail

from taiping.constants import GenderChoices
from taiping.models import EmailVerification


UserType: TypeAlias = Literal["student", "instructor"]


class CreateAccountView(View):

    def get(self, request: HttpRequest, user_type: UserType="student") -> HttpResponse:
        gender_options: list[tuple[str, str]] = list(cast(Any, GenderChoices.choices))
        return render(request, f"taiping/create_account/{ user_type }.html", locals())

    def get_verification_code(self, request: HttpRequest) -> HttpResponse:
        verification_code: str = EmailVerification.gen_code()
        EmailVerification.objects.update_or_create(
            email=request.POST["email"].lower(),
            defaults={ "code": verification_code },
        )
        send_mail(
            subject="Agojin Email Verification",
            message=f"Your Agojin email verification code is {verification_code}.",
            from_email=None,
            recipient_list=[request.POST["email"]],
            fail_silently=False,
        )
        return render(request, "taiping/create_account/verification_code.html", locals())

    def post(self, request: HttpRequest, user_type: UserType="student") -> HttpResponse:
        htmx: str = request.GET.get("htmx", "")

        if htmx == "get-verification-code":
            return self.get_verification_code(request)
        if htmx == "verify-code":
            return self.verify_code(request)

        raise NotImplementedError

    def verify_code(self, request: HttpRequest) -> HttpResponse:
        verification_code: str = request.POST["email_verification_code"]
        verified: EmailVerification | None = (EmailVerification.objects
            .filter(
                email=request.POST["email"].lower(),
                code=verification_code,
            ).first()
        )
        return render(request, "taiping/create_account/verify_code.html", locals())

