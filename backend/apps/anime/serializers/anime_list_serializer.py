from rest_framework import serializers


class AnimeListSerializer(serializers.Serializer):

    search = serializers.CharField(
        required=False,
        allow_blank=True
    )

    status_id = serializers.IntegerField(
        required=False,
        allow_null=True
    )

    delete_status = serializers.BooleanField(
        required=False
    )

    order_by = serializers.CharField(
        required=False,
        default="created_at"
    )

    order_type = serializers.ChoiceField(
        choices=["asc", "desc"],
        default="desc"
    )

    page = serializers.IntegerField(
        min_value=1,
        default=1
    )
