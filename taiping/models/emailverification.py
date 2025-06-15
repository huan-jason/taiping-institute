from random import randint

from django.db.models import (
    CharField,
    EmailField,
)
from .basemodel import BaseModel


class EmailVerification(BaseModel):
    email = EmailField(unique=True)
    code = CharField(max_length=4)

    def __str__(self) -> str:
        return self.email

    @classmethod
    def gen_code(cls) -> str:
        return str(randint(1000, 9999))
