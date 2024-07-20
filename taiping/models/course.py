from django.db.models import (
    CharField,
    DateField,
    IntegerField,
    TextField,
)
from .basemodel import BaseModel


class Course(BaseModel):
    name = CharField(max_length=128, unique=True)
    description = TextField()
    course_fee = IntegerField()
    min_students = IntegerField()
    max_students = IntegerField()
    next_class = DateField()

    def __str__(self) -> str:
        return self.name
