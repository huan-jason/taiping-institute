import logging
from typing import Any, cast

from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import QuerySet
from django.template.loader import render_to_string
from django.utils import timezone

from taiping.constants import CourseStatusChoices
from taiping.models import CourseClass


class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write(f"{timezone.now()}")

        queryset: QuerySet[CourseClass] = (CourseClass.objects
            .select_related("course")
            .filter(
                started=False,
                auto_start=True,
                status=CourseStatusChoices.PUBLISHED,
            )
        )

        for item in queryset:

            if item.students.count() < item.min_students:
                continue

            self.stdout.write(
                f"Auto starting course {item.course.name} "
                f"({item.start_date})"
            )

            item.started = True

            with transaction.atomic():
                self.send_emails(item)
                item.save()

    def send_emails(self, course_class: CourseClass) -> None:
        msg_text: str = render_to_string(
            template_name="taiping/auto_start/index.txt",
            context=locals(),
        )
        msg_html: str = render_to_string(
            template_name="taiping/auto_start/index.html",
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
            cc=[course_class.get_instructor.user.email],
            body=msg_text,
        )
        email.attach_alternative(msg_html, "text/html")
        email.send()
