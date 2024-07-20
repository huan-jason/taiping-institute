from django.db.models import (
    CharField,
    IntegerField,
    TextField,
)
from .basemodel import BaseModel


class CourseGroup(BaseModel):
    name = CharField(max_length=128, unique=True)
    description = TextField()
    sort_order = IntegerField(default=999)

    def __str__(self) -> str:
        return self.name
