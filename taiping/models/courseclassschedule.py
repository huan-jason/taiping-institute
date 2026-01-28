from django.db.models import (
    DateField,
    ForeignKey,
    PROTECT,
    TextField,
    TimeField,
    UniqueConstraint,
)
from .basemodel import BaseModel


class CourseClassSchedule(BaseModel):
    course_class = ForeignKey('taiping.CourseClass', on_delete=PROTECT)
    class_date = DateField(db_index=True)
    class_time_start = TimeField(db_index=True)
    class_time_end = TimeField(db_index=True)
    notes = TextField(null=True, blank=True)

    class Meta:  # type: ignore
        constraints = [
            UniqueConstraint(
                name="course_class_schedule__unique",
                fields=[
                    "course_class",
                    "class_date",
                    "class_time_start",
                    "class_time_end",
                ],
            )
        ]

    def __str__(self) -> str:
        return f"{self.course_class} :: {self.class_date} :: {self.class_time_start} :: {self.class_time_end}"

    @property
    def time(self) -> str:
        return f"{self.class_time_start:%H:%M} - {self.class_time_end:%H:%M}"
