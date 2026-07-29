from rest_framework.views import APIView

from apps.expense.services.expense_service import ExpenseService

from common.responses import SuccessResponse


class ExpenseTimelineMonthView(
    APIView
):

    service = ExpenseService()

    def post(
        self,
        request
    ):

        year = request.data.get(
            "year"
        )

        data = self.service.timeline_months(
            request.user,
            year
        )

        return SuccessResponse(
            data=data
        )
