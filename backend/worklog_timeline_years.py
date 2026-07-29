from rest_framework.views import APIView

from apps.worklog.services.worklog_service import WorkLogService

from common.responses import SuccessResponse
from common.messages import Messages
from common.status_codes import StatusCode


class WorkLogTimelineYearsView(APIView):

    service = WorkLogService()

    def post(self, request):

        years = self.service.get_timeline_years(
            request.user
        )

        return SuccessResponse(

            message=Messages.SUCCESS,

            data={
                "years": years
            },

            status_code=StatusCode.OK

        )
