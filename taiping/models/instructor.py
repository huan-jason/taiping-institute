from datetime import date
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

    @property
    def students(self) -> QuerySet[CourseClassStudent]:
        from .courseclassstudent import CourseClassStudent  # noqa

        return CourseClassStudent.objects.filter(
            course_class__instructor=self,
        )
