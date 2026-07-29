from rest_framework import serializers


class WorkLogTimelineYearSerializer(
    serializers.Serializer
):

    year = serializers.IntegerField(
        min_value=1900,
        max_value=9999
    )
