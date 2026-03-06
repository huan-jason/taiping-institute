from django.db.models import (
    ForeignKey,
    PROTECT,
    UniqueConstraint,
)
from .basemodel import BaseModel


class CourseClassStudentSession(BaseModel):
    course_class_student = ForeignKey('taiping.CourseClassStudent', on_delete=PROTECT)
    course_class_schedule = ForeignKey('taiping.CourseClassSchedule', on_delete=PROTECT)

    class Meta:  # type: ignore
        constraints = [
            UniqueConstraint(
                name="%(app_label)s_%(class)s__unique",
                fields=[
                    "course_class_student",
                    "course_class_schedule",
                ],
            ),
        ]

    def __str__(self) -> str:
        return f"{self.course_class_student} :: {self.course_class_schedule}"
