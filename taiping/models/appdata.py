from django.db.models import (
    CharField,
    TextField,
)
from .basemodel import BaseModel


class AppData(BaseModel):
    name = CharField(max_length=128, unique=True)
    data = TextField()

    class Meta:  # type: ignore
        verbose_name_plural = "App data"

    def __str__(self) -> str:
        return self.name
