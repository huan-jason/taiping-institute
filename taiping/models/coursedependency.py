from django.db.models import (
    ForeignKey,
    PROTECT,
    UniqueConstraint,
)
from .basemodel import BaseModel


class CourseDependency(BaseModel):
    course = ForeignKey('taiping.Course', on_delete=PROTECT)
    dependent_course = ForeignKey('taiping.Course', on_delete=PROTECT, related_name="+")

    class Meta: # type: ignore
        verbose_name_plural = "Course dependencies"
        constraints = [
            UniqueConstraint(
                name="course_dependency__unique",
                fields=["course", "dependent_course"],
            )
        ]

    def __str__(self) -> str:
        return f"{self.course} :: {self.course.name} :: {self.dependent_course.name}"
