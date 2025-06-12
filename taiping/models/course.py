from markdown import markdown # type: ignore

from django.db.models import (
    CharField,
    FileField,
    ForeignKey,
    IntegerField,
    PROTECT,
    TextField,
)
from .basemodel import BaseModel


class Course(BaseModel):
    course_group = ForeignKey('taiping.CourseGroup', on_delete=PROTECT, null=True, blank=True)
    name = CharField(max_length=128, unique=True)
    chinese_name = CharField(max_length=128, unique=True, null=True)
    description = TextField()
    short_description = TextField(default="")
    default_course_fee = IntegerField(null=True, blank=True)
    default_min_students = IntegerField(null=True, blank=True)
    default_max_students = IntegerField(null=True, blank=True)
    default_instructor = ForeignKey("taiping.Instructor", on_delete=PROTECT, null=True, blank=True)
    default_facility = ForeignKey("taiping.Facility", on_delete=PROTECT, null=True, blank=True)
    sort_order = IntegerField(default=999)
    image = FileField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    @property
    def description_md(self) -> str:
        return markdown(self.description)

    @property
    def short_description_md(self) -> str:
        return markdown(self.short_description)
