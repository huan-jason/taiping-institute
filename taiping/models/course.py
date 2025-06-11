from django.db.models import (
    CharField,
    FileField,
    ForeignKey,
    IntegerField,
    PROTECT,
    TextField,
    UniqueConstraint,
)
from .basemodel import BaseModel


class Course(BaseModel):
    course_group = ForeignKey('taiping.CourseGroup', on_delete=PROTECT, null=True, blank=True)
    name = CharField(max_length=128, unique=True)
    description = TextField()
    sort_order = IntegerField(default=999)
    image = FileField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name
