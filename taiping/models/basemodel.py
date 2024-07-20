from django.db.models import (
    DateTimeField,
    Model,
)


class BaseModel(Model):
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    class Meta:
        abstract = True

