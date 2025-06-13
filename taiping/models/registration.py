from django.db.models import (
    BooleanField,
    ForeignKey,
    PROTECT,
    TextField,
    UniqueConstraint,
)
from .basemodel import BaseModel


class Registration(BaseModel):
    course_class = ForeignKey('taiping.CourseClass', on_delete=PROTECT)
    student = ForeignKey('auth.User', on_delete=PROTECT)
    started = BooleanField(default=False, db_index=True)
    completed = BooleanField(default=False, db_index=True)
    comments = TextField(null=True, blank=True)

    class Meta: # type: ignore
        constraints = [
            UniqueConstraint(
                name="registration__unique",
                fields=["course_class", "student"],
            )
        ]

    def __str__(self) -> str:
        return f"{self.course_class.course.name} :: {self.student.username}"
