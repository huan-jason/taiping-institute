from typing import TYPE_CHECKING
from django.db.models import (
    CharField,
    DateField,
    FileField,
    IntegerField,
    OneToOneField,
    PROTECT,
    QuerySet,
    TextField,
)
from taiping.constants import GenderChoices
from .basemodel import BaseModel

from taiping.constants import CourseStudentStatusChoices

if TYPE_CHECKING:
    from .courseclassstudent import CourseClassStudent
    from .courseclassstudentsession import CourseClassStudentSession


class Student(BaseModel):
    user = OneToOneField('auth.User', on_delete=PROTECT)
    alternative_name = CharField(max_length=128, db_index=True, null=True, blank=True)
    comments = TextField(null=True, blank=True)
    date_of_birth = DateField(db_index=True)
    gender = CharField(max_length=8, choices=GenderChoices, null=True, blank=True, db_index=True)
    phone = CharField(max_length=128)
    photo = FileField(upload_to="student/", null=True, blank=True)
    experience_years = IntegerField(default=0, blank=True)
    styles_trained = TextField(null=True, blank=True)
    medical_conditions = TextField(null=True, blank=True)
    preferred_languages = TextField(null=True, blank=True)
    emergency_contact_name = CharField(max_length=128, null=True, blank=True)
    emergency_contact_phone = CharField(max_length=128, null=True, blank=True)

    def __str__(self) -> str:
        return self.user.username

    def attendance_pct(self) -> float:
        from .courseclassstudent import CourseClassStudent
        from .courseclassschedule import CourseClassSchedule

        course_class_ids: list[int] = list(CourseClassStudent.objects
            .filter(student=self)
            .values_list("course_class_id", flat=True)
        )
        course_class_schedules: QuerySet[CourseClassSchedule] = (CourseClassSchedule.objects
            .filter(course_class_id__in=course_class_ids)
        )
        return self.sessions().count() / course_class_schedules.count()

    def courses_completed(self) -> QuerySet[CourseClassStudent]:
        return (self
            .courseclassstudent_set  # type: ignore
            .filter(status=CourseStudentStatusChoices.COMPLETED)
            .order_by("-created")
        )

    def courses_enrolled(self) -> QuerySet[CourseClassStudent]:
        return (self
            .courseclassstudent_set  # type: ignore
            .order_by("-created")
        )

    def sessions(self) -> QuerySet[CourseClassStudentSession]:
        from .courseclassstudentsession import CourseClassStudentSession

        return CourseClassStudentSession.objects.filter(
            course_class_student__student=self,
        )
