import logging
from typing import Optional

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
    sort_order = IntegerField(null=True, blank=True, default=999)
    image = URLField(null=True, blank=True)
    static_url = CharField(max_length=1024, null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    def dependencies(self,
        results: dict[int, 'Course'] | None = None,
        course: Optional['Course'] = None,
    ) -> dict[int, 'Course']:

        results = results or {}
        course = course or self

        for obj in course.coursedependency_set.all():
            if obj.id in results:
                logging.warning(f"Course already in prerequesites: {obj.id}")
                continue

            results[obj.id] = obj.dependent_course
            results |= self.dependencies(results, obj.dependent_course)

        return results
