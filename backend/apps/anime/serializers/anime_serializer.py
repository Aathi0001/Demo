from rest_framework import serializers

from apps.anime.models import Anime


class AnimeSerializer(serializers.ModelSerializer):

    class Meta:

        model = Anime

        fields = [

            "anime_name",

            "status",

            "updated_till",

            "watched_episode",

            "notes",

        ]

    def validate_anime_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Anime name cannot be empty."
            )

        return value
