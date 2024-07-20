from django.db.models import (
    BooleanField,
    CharField,
    EmailField,
    ForeignKey,
    IntegerField,
    PROTECT,
    TextField,
    UniqueConstraint,
)
from .basemodel import BaseModel


class Student(BaseModel):
    course_class = ForeignKey('taiping.CourseClass', on_delete=PROTECT)
    registration = ForeignKey('taiping.Registration', on_delete=PROTECT, null=True, blank=True)
    non_registration_id = IntegerField(null=True, blank=True)
    paid = BooleanField(default=False)
    comments = TextField(null=True, blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                name="student__unique",
                fields=["course_class", "registration", "non_registration_id"],
            )
        ]

    def __str__(self) -> str:
        return f"{self.course_class} :: {self.registration} :: {self.non_registration_id}"
