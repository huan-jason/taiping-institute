from django.db.models import (
    CharField,
    ForeignKey,
    PROTECT,
    UniqueConstraint,
)
from taiping.constants import CourseStudentStatusChoices
from .basemodel import BaseModel


class CourseClassStudent(BaseModel):
    course_class = ForeignKey('taiping.CourseClass', on_delete=PROTECT)
    student = ForeignKey('taiping.Student', on_delete=PROTECT)
    status = CharField(max_length=16, choices=CourseStudentStatusChoices, db_index=True, default=CourseStudentStatusChoices.ENROLLED)

    class Meta:  # type: ignore
        constraints = [
            UniqueConstraint(
                name="%(app_label)s_%(class)s__unique",
                fields=["course_class", "student"],
            )
        ]

    def __str__(self) -> str:
        return f"{self.course_class} :: {self.student}"
