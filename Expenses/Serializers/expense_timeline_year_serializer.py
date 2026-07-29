from rest_framework import serializers


class ExpenseTimelineYearSerializer(
    serializers.Serializer
):

    year = serializers.IntegerField()

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
