from rest_framework import serializers


class WorkLogTimelineWeekSerializer(
    serializers.Serializer
):

    week_start = serializers.DateField()

    week_end = serializers.DateField()

    week_offset = serializers.IntegerField()

    log_count = serializers.IntegerField()


class WorkLogTimelineMonthSerializer(
    serializers.Serializer
):

    month = serializers.IntegerField()

    month_name = serializers.CharField()

    total_logs = serializers.IntegerField()

    weeks = WorkLogTimelineWeekSerializer(
        many=True
    )


class WorkLogTimelineSerializer(
    serializers.Serializer
):

    year = serializers.IntegerField()

    months = WorkLogTimelineMonthSerializer(
        many=True
    )
