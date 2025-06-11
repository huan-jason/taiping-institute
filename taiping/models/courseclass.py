from django.db.models import (
    BooleanField,
    CharField,
    DateField,
    ForeignKey,
    IntegerField,
    PROTECT,
    TextField,
    UniqueConstraint,
)
from taiping.constants import CourseStatusChoices
from .basemodel import BaseModel


class CourseClass(BaseModel):
    course = ForeignKey('taiping.Course', on_delete=PROTECT)
    notes = TextField(null=True, blank=True)
    course_fee = IntegerField()
    min_students = IntegerField()
    max_students = IntegerField()
    instructor = ForeignKey("taiping.Instructor", on_delete=PROTECT)
    facility = ForeignKey("taiping.Facility", on_delete=PROTECT)
    start_date = DateField(db_index=True)
    end_date = DateField(db_index=True)
    status = CharField(max_length=32, db_index=True, choices=CourseStatusChoices, default=CourseStatusChoices.DRAFT)
    auto_start = BooleanField(default=False)

    class Meta: # type: ignore
        verbose_name_plural = "Course classes"
        constraints = [
            UniqueConstraint(
                name="course_class__unique",
                fields=["course", "start_date", "instructor"],
            )
        ]

    def __str__(self) -> str:
        return f"{self.course} :: {self.start_date} :: {self.instructor}"
