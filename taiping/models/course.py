from django.db.models import (
    CharField,
    FileField,
    ForeignKey,
    IntegerField,
    PROTECT,
    QuerySet,
    TextField,
)
from django.utils import timezone

from taiping.constants import CourseStatusChoices
from .basemodel import BaseModel


class Course(BaseModel):
    course_group = ForeignKey('taiping.CourseGroup', on_delete=PROTECT, null=True, blank=True)
    name = CharField(max_length=128, unique=True)
    chinese_name = CharField(max_length=128, unique=True, null=True)
    description = TextField()
    short_description = TextField(default="")
    course_fee = IntegerField(null=True, blank=True)
    min_students = IntegerField(null=True, blank=True)
    max_students = IntegerField(null=True, blank=True)
    instructor = ForeignKey("taiping.Instructor", on_delete=PROTECT, null=True, blank=True)
    facility = ForeignKey("taiping.Facility", on_delete=PROTECT, null=True, blank=True)
    sort_order = IntegerField(default=999)
    image = FileField(upload_to="course/", null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    def upcoming_classes(self) -> QuerySet:
        return (self.courseclass_set  # type: ignore
            .filter(
                start_date__gte=timezone.now(),
                status=CourseStatusChoices.PUBLISHED,
            )
        )
