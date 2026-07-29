from rest_framework.views import APIView

from apps.expense.services.expense_service import ExpenseService

from common.responses import SuccessResponse


class ExpenseTimelineYearView(
    APIView
):

    service = ExpenseService()

    def post(
        self,
        request
    ):

        data = self.service.timeline_years(
            request.user
        )

        return SuccessResponse(
            data=data
        )
