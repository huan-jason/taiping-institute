from django.db.models import (
    ForeignKey,
    PROTECT,
)
from .basemodel import BaseModel


class CourseDependency(BaseModel):
    course = ForeignKey('taiping.Course', on_delete=PROTECT)
    dependent_course = ForeignKey('taiping.Course', on_delete=PROTECT, related_name="+")

    def __str__(self) -> str:
        return self.course.name
