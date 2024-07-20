from django.db.models import (
    CharField,
    EmailField,
    ForeignKey,
    PROTECT,
    TextField,
    UniqueConstraint,
)
from .basemodel import BaseModel


class Registration(BaseModel):
    course = ForeignKey('taiping.Course', on_delete=PROTECT)
    name = CharField(max_length=128, db_index=True)
    email = EmailField(db_index=True)
    tel = CharField(max_length=32)
    comments = TextField(null=True, blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                name="registration__unique",
                fields=["course", "email"],
            )
        ]

    def __str__(self) -> str:
        return f"{self.course} :: {self.name} :: {self.email}"
