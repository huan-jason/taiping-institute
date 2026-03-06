from datetime import date, timedelta
from functools import cache
from typing import TYPE_CHECKING

from django.db.models import (
    BooleanField,
    CharField,
    DateField,
    FileField,
    OneToOneField,
    PROTECT,
    QuerySet,
    TextField,
)
from django.utils import timezone

from taiping.constants import CourseStudentStatusChoices
from .basemodel import BaseModel

if TYPE_CHECKING:
    from .courseclass import CourseClass
    from .courseclassstudent import CourseClassStudent


class Instructor(BaseModel):
    user = OneToOneField('auth.User', on_delete=PROTECT)
    alternative_name = CharField(max_length=128, db_index=True, null=True, blank=True)
    bio = TextField()
    certifications = TextField()
    photo = FileField(upload_to="instructor/", null=True, blank=True)
    verified = BooleanField(default=False, db_index=True)
    calendar_sync = BooleanField(default=False, db_index=True)
    date_joined = DateField(db_index=True)
    position = CharField(max_length=64, db_index=True, null=True, blank=True)

    def __str__(self) -> str:
        return self.user.username

    @property
    def courses_active(self) -> QuerySet[CourseClass]:
        from .courseclass import CourseClass  # noqa

        today: date = timezone.now().date()
        return CourseClass.objects.filter(
            instructor=self,
            start_date__lte=today,
            end_date__gte=today,
        )

    @property
    def courses_all(self) -> QuerySet[CourseClass]:
        from .courseclass import CourseClass  # noqa

        return CourseClass.objects.filter(
            instructor=self,
        )

    @property
    def courses_upcoming(self) -> QuerySet[CourseClass]:
        from .courseclass import CourseClass  # noqa

        today: date = timezone.now().date()
        return CourseClass.objects.filter(
            instructor=self,
            start_date__gt=today,
        )

    @cache
    def get_revenue(self, month: date | None = None) -> float:
        from .courseclassstudent import CourseClassStudent  # noqa

        month = month or timezone.now().date()
        qs: QuerySet[CourseClassStudent] = (CourseClassStudent.objects
            .filter(
                course_class__instructor=self,
                course_class__start_date__year=month.year,
                course_class__start_date__month=month.month,
            )
            .exclude(status=CourseStudentStatusChoices.CANCELLED)
            .select_related("course_class")
        )
        return sum([
            item.course_class.get_course_fee()
            for item in qs
        ])

    @property
    def revenue(self) -> float:
        return self.get_revenue()

    @property
    @cache
    def revenue_delta_pct(self, month: date | None = None) -> float:
        prev_month: date = (timezone.now().replace(day=1) - timedelta(days=1)).date()
        curr_revenue: float = self.get_revenue()
        prev_revenue: float = self.get_revenue(prev_month)

        if not prev_revenue: return 100
        return 100 * (curr_revenue - prev_revenue) / prev_revenue

    @property
    def students(self) -> QuerySet[CourseClassStudent]:
        from .courseclassstudent import CourseClassStudent  # noqa

        return (CourseClassStudent.objects
            .filter(course_class__instructor=self)
            .exclude(status=CourseStudentStatusChoices.CANCELLED)
        )

    @property
    def week_sessions(self, date_: date | None = None) -> int:
        from .courseclassschedule import CourseClassSchedule  # noqa

        date_ = date_ or timezone.now().date()
        week_start: date = date_ - timedelta(days=date_.isoweekday())
        week_end: date = week_start + timedelta(days=6)

        return (CourseClassSchedule.objects
            .filter(
                course_class__instructor=self,
                class_date__range=[week_start, week_end],
            )
            .count()
        )
