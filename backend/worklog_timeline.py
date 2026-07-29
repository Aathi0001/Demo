from rest_framework.views import APIView

from apps.worklog.serializers.worklog_timeline_year_serializer import (
    WorkLogTimelineYearSerializer
)

from apps.worklog.services.worklog_service import WorkLogService

from common.responses import SuccessResponse
from common.responses import ErrorResponse

from common.messages import Messages
from common.status_codes import StatusCode


class WorkLogTimelineView(APIView):

    service = WorkLogService()

    def post(self, request):

        serializer = WorkLogTimelineYearSerializer(

            data=request.data

        )

        if not serializer.is_valid():

            return ErrorResponse(

                message=Messages.VALIDATION_ERROR,

                errors=serializer.errors,

                status_code=StatusCode.BAD_REQUEST

            )

        timeline = self.service.get_timeline(

            request.user,

            serializer.validated_data["year"]

        )

        return SuccessResponse(

            message=Messages.SUCCESS,

            data=timeline,

            status_code=StatusCode.OK

        )
