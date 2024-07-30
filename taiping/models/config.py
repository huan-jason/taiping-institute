from django.db.models import (
    CharField,
    QuerySet,
    TextField,
)
from .basemodel import BaseModel


class Config(BaseModel):
    name = CharField(max_length=128, db_index=True)
    value = TextField()
    description = TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.name} :: {self.value}"

    @classmethod
    def registration_notification(cls) -> QuerySet:
        return cls.objects.filter(name="registration_notification")
