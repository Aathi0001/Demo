from django.db import models

from .base_model import BaseModel


class SoftDeleteModel(BaseModel):

    delete_status = models.BooleanField(
        default=False
    )

    deleted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:

        abstract = True
