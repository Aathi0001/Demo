from django.db import models
from django.contrib.auth.models import User

from apps.common.models.soft_delete_model import SoftDeleteModel

from .anime_status import AnimeStatus


class Anime(SoftDeleteModel):

    anime_id = models.AutoField(
        primary_key=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="animes"
    )

    anime_name = models.CharField(
        max_length=255,
        db_index=True
    )

    status = models.ForeignKey(
        AnimeStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="animes"
    )

    updated_till = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    watched_episode = models.PositiveIntegerField(
        default=0
    )

    notes = models.TextField(
        blank=True
    )

    class Meta:

        db_table = "anime"

        constraints = [

            models.UniqueConstraint(
                fields=["user", "anime_name"],
                name="unique_user_anime"
            )

        ]

        ordering = [
            "-created_at"
        ]

    def __str__(self):

        return self.anime_name
