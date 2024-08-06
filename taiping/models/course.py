from typing import Optional

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

    def met_prerequisites(self, email: str) -> bool:
        from taiping.models import Student

        student_courses: set[int] = set(Student.objects
            .filter(
                registration__email=email,
                registration__course=self,
            )
            .values_list("course_class__course_id", flat=True)
        )
        if not student_courses: return False

        prerequisite_course_ids: set[int] = {
            item.id for item in self.prerequisites()
        }
        return student_courses >= prerequisite_course_ids

    @property
    def name_1(self) -> str:
        return self.name.split("|")[0]

    @property
    def name_2(self) -> str:
        return self.name.split("|")[-1]

    def prerequisites(self,
        course: Optional['Course'] = None,
        course_dependencies: list['Course'] | None = None,
    ) -> list['Course']:

        course = course or self
        queryset: QuerySet = course.coursedependency_set.all()
        if not queryset.count():
            return []

        course_dependencies = course_dependencies or []
        for obj in queryset:
            obj_dependencies = self.prerequisites(obj.dependent_course, course_dependencies)
            obj_dependencies.append(obj.dependent_course)
            course_dependencies += obj_dependencies

        return course_dependencies

    def prerequisite_course_ids(self, course: Optional['Course'] = None) -> set[int]:
        course = course or self
        queryset: QuerySet = course.coursedependency_set.all()
        if not queryset.count():
            return set()

        course_ids: set[int] = set()

        for obj in queryset:
            obj_course_ids: set[int] = self.prerequisite_course_ids(obj.dependent_course)
            obj_course_ids.add(obj.dependent_course.id)
            course_ids |= obj_course_ids

        return course_ids
