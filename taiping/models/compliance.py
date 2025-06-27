from typing import Any, cast
from django.db.models import (
    CharField,
    ForeignKey,
    PROTECT,
    TextField,
)

from taiping.constants import ComplianceTypeChoices
from .basemodel import BaseModel


class Compliance(BaseModel):
    student = ForeignKey("taiping.Student", on_delete=PROTECT, null=True, blank=True)
    instructor = ForeignKey("taiping.Instructor", on_delete=PROTECT, null=True, blank=True)
    compliance_type = CharField(max_length=32, choices=ComplianceTypeChoices, db_index=True)
    data = TextField()

    def __str__(self) -> str:
        return f"{self.compliance_type} :: {cast(Any, self.student).user.get_full_name()}"
