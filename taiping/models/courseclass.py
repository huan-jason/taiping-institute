from typing import Any, cast
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
    started = BooleanField(default=False, db_index=True)
    auto_start = BooleanField(default=False, db_index=True)

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

    @property
    def get_course_fee(self) -> int:
        return cast(Any, self.course_fee or self.course.course_fee)

    @property
    def get_min_students(self) -> int:
        return cast(Any, self.min_students or self.course.min_students)

    @property
    def get_max_students(self) -> int:
        return cast(Any, self.max_students or self.course.max_students)

    @property
    def get_instructor(self) -> Any:
        return cast(Any, self.instructor or self.course.instructor)

    @property
    def get_facility(self) -> Any:
        return self.facility or self.course.facility
