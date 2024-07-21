from django.db.models import (
    CharField,
    DateField,
    ForeignKey,
    IntegerField,
    PROTECT,
    TextField,
    URLField,
)
from .basemodel import BaseModel


class Course(BaseModel):
    course_group = ForeignKey('taiping.CourseGroup', on_delete=PROTECT)
    name = CharField(max_length=128, unique=True)
    description = TextField()
    course_fee = IntegerField()
    min_students = IntegerField()
    max_students = IntegerField(null=True, blank=True)
    next_class = DateField(null=True, blank=True)
    sort_order = IntegerField(default=999)
    image = URLField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name
