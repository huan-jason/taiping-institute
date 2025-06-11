from django.db.models import (
    BooleanField,
    CharField,
    EmailField,
    TextField,
)

from .basemodel import BaseModel


class Facility(BaseModel):
    name = CharField(max_length=128, unique=True)
    description = TextField()
    address = TextField()
    coordinated = CharField(max_length=32, blank=True, null=True)
    contact_name = CharField(max_length=128)
    contact_phone = CharField(max_length=128)
    contact_email = EmailField()
    approved = BooleanField(default=False)

    def __str__(self) -> str:
        return self.name
