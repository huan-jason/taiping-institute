from django.db.models import (
    CharField,
    DateField,
    FileField,
    IntegerField,
    OneToOneField,
    PROTECT,
    TextField,
)
from taiping.constants import GenderChoices
from .basemodel import BaseModel


class Student(BaseModel):
    user = OneToOneField('auth.User', on_delete=PROTECT)
    alternative_name = CharField(max_length=128, db_index=True, null=True, blank=True)
    comments = TextField(null=True, blank=True)
    date_of_birth = DateField(db_index=True)
    gender = CharField(max_length=8, choices=GenderChoices, null=True, blank=True, db_index=True)
    phone = CharField(max_length=128)
    profile_photo = FileField(upload_to="student/", null=True, blank=True)
    experience_years = IntegerField(default=0, blank=True)
    styles_trained = TextField(null=True, blank=True)
    medical_conditions = TextField(null=True, blank=True)
    preferred_languages = TextField(null=True, blank=True)
    emergency_contact_name = CharField(max_length=128, null=True, blank=True)
    emergency_contact_phone = CharField(max_length=128, null=True, blank=True)

    def __str__(self) -> str:
        return self.user.username
