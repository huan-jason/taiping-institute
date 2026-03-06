from datetime import date, timedelta
from typing import Any, cast

from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction
from django.db.models import QuerySet
from django.template.loader import render_to_string
from django.utils import timezone

from taiping.constants import CourseStatusChoices
from taiping.models import CourseClass, Registration


class Command(BaseCommand):

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("-d", "--days-before_start", type=int, default=0)

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write(f"{timezone.now()}")

        cut_off_date: date = timezone.now().date() - timedelta(days=options["days_before_start"])

        queryset: QuerySet[CourseClass] = (CourseClass.objects
            .select_related("course")
            .filter(
                started=False,
                status=CourseStatusChoices.PUBLISHED,
                start_date__lte=cut_off_date,
            )
        )

        for item in queryset:

            if item.students.count() >= item.min_students:
                continue

            self.stdout.write(
                f"Expiring class {item.course.name} "
                f"({item.start_date})"
            )

            item.status = CourseStatusChoices.CANCELLED

            with transaction.atomic():
                self.send_emails(item)
                item.save()

            self.refund(item)

    def send_emails(self, course_class: CourseClass) -> None:
        msg_text: str = render_to_string(
            template_name="taiping/class_expiry/index.txt",
            context=locals(),
        )
        msg_html: str = render_to_string(
            template_name="taiping/class_expiry/index.html",
            context=locals(),
        )
        subject: str = (
            f"Course {course_class.course.name} "
            f"{course_class.course.chinese_name}"
        )
        students: list[str] = [
            item.student.user.email
            for item in cast(Any, course_class).registration_set
                .select_related("student__user")
                .all()
        ]

        email: EmailMultiAlternatives = EmailMultiAlternatives(
            subject=subject,
            from_email=None,
            to=students,
            cc=[course_class.get_instructor().user.email],
            body=msg_text,
        )
        email.attach_alternative(msg_html, "text/html")
        email.send()

    def send_email_refund(self, registration: Registration) -> None:
        msg_text: str = render_to_string(
            template_name="taiping/class_expiry/refund.txt",
            context=locals(),
        )
        msg_html: str = render_to_string(
            template_name="taiping/class_expiry/refund.html",
            context=locals(),
        )
        subject: str = (
            f"Course Refund: {registration.course_class.course.name} "
            f"{registration.course_class.course.chinese_name}"
        )

        email: EmailMultiAlternatives = EmailMultiAlternatives(
            subject=subject,
            from_email=None,
            to=[registration.student.user.email],
            cc=[registration.course_class.get_instructor().user.email],
            body=msg_text,
        )
        email.attach_alternative(msg_html, "text/html")
        email.send()

    def refund(self, course_class: CourseClass) -> None:

        for item in (cast(Any, course_class).registration_set
            .select_related("student__user")
            .all()
        ):
            with transaction.atomic():
                self.refund_student(item)
                self.send_email_refund(item)
                self.stdout.write(f"Refunded {item.student.user.email}")

    def refund_student(self, registration: Registration) -> None:
        print(f"Refunding {registration.student.user.email} (TO DO)")  # zzz
