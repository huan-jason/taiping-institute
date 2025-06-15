from django.db.models import (
    BooleanField,
    DateField,
    FileField,
    OneToOneField,
    PROTECT,
    TextField,
)

from .basemodel import BaseModel


class Instructor(BaseModel):
    user = OneToOneField('auth.User', on_delete=PROTECT)
    bio = TextField()
    certifications = TextField()
    photo = FileField(upload_to="instructor/", null=True, blank=True)
    verified = BooleanField(default=False, db_index=True)
    calendar_sync = BooleanField(default=False, db_index=True)
    date_joined = DateField(db_index=True)

    def __str__(self) -> str:
        return self.user.username
