from django.db.models import (
    CharField,
    DateTimeField,
    ForeignKey,
    PROTECT,
    TextField,
    UniqueConstraint,
)
from .basemodel import BaseModel

class CourseClass(BaseModel):
    course = ForeignKey('taiping.Course', on_delete=PROTECT)
    name = CharField(max_length=128, db_index=True)
    notes = TextField(null=True, blank=True)
    start_date = DateTimeField(db_index=True)
    end_date = DateTimeField(db_index=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Course classes"
        constraints = [
            UniqueConstraint(
                name="course_class__unique",
                fields=["course", "name"],
            )
        ]

    def __str__(self) -> str:
        return f"{self.course} :: {self.name}"
