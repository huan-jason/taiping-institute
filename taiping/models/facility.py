from django.db.models import (
    BooleanField,
    CharField,
    EmailField,
    TextField,
)

from .basemodel import BaseModel


class Facility(BaseModel):
    name = CharField(max_length=128, unique=True)
    description = TextField(null=True, blank=True)
    address = TextField(null=True, blank=True)
    coordinated = CharField(max_length=32, blank=True, null=True)
    contact_name = CharField(max_length=128)
    contact_phone = CharField(max_length=128)
    contact_email = EmailField()
    approved = BooleanField(default=False)

    class Meta: # type: ignore
        verbose_name_plural = "facilities"


    def __str__(self) -> str:
        return self.name
