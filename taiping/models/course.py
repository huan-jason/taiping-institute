from typing import Optional, TypedDict

from django.db.models import (
    CharField,
    DateField,
    ForeignKey,
    IntegerField,
    PROTECT,
    QuerySet,
    TextField,
    URLField,
)

from .basemodel import BaseModel


class DependentCourse(TypedDict):
    id: int
    name: str


class Course(BaseModel):
    course_group = ForeignKey('taiping.CourseGroup', on_delete=PROTECT)
    name = CharField(max_length=128, unique=True)
    description = TextField()
    course_fee = IntegerField()
    min_students = IntegerField()
    max_students = IntegerField(null=True, blank=True)
    next_class = DateField(null=True, blank=True)
    sort_order = IntegerField(null=True, blank=True, default=999)
    image = URLField(null=True, blank=True)
    static_url = CharField(max_length=1024, null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    def prerequisites(self,
        course: Optional['Course'] = None,
        course_dependencies: list[DependentCourse] | None = None,
    ) -> list[DependentCourse]:

        course = course or self
        queryset: QuerySet = course.coursedependency_set.all()
        if not queryset.count():
            return []

        course_dependencies = course_dependencies or []
        for obj in queryset:
            obj_dependencies = self.prerequisites(obj.dependent_course, course_dependencies)
            obj_dependencies.append({
                "id": obj.dependent_course.id,
                "name": obj.dependent_course.name,
            })
            course_dependencies += obj_dependencies

        return course_dependencies
