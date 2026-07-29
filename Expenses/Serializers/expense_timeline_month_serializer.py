from rest_framework import serializers


class ExpenseTimelineMonthSerializer(
    serializers.Serializer
):

    month = serializers.IntegerField()

    month_name = serializers.CharField()

    expense_count = serializers.IntegerField()

    total_credit = serializers.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    total_debit = serializers.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    net_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    month_offset = serializers.IntegerField()
