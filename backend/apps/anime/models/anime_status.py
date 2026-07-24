from django.db import models
from django.contrib.auth.models import User

from apps.common.models.base_model import BaseModel


class AnimeStatus(BaseModel):

    status_id = models.AutoField(
        primary_key=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="anime_statuses"
    )

    status_name = models.CharField(
        max_length=100
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:

        db_table = "anime_status"

        constraints = [

            models.UniqueConstraint(
                fields=["user", "status_name"],
                name="unique_user_anime_status"
            )

        ]

        ordering = [
            "status_name"
        ]

    def __str__(self):

        return self.status_name
