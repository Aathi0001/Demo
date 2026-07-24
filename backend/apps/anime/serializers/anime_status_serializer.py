from rest_framework import serializers

from apps.anime.models import AnimeStatus


class AnimeStatusSerializer(serializers.ModelSerializer):

    class Meta:

        model = AnimeStatus

        fields = [

            "status_name",

            "is_active",

        ]

    def validate_status_name(self, value):

        value = value.strip()

        if not value:

            raise serializers.ValidationError(
                "Status name cannot be empty."
            )

        return value
