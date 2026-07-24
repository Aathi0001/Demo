from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from accounts.serializers.refresh_serializer import RefreshSerializer
from accounts.services.auth_service import AuthService
from common.messages import Messages
from common.responses import ApiResponse
from common.status_codes import StatusCode


class RefreshView(APIView):

    permission_classes = [AllowAny]

    auth_service = AuthService()

    def post(self, request):

        serializer = RefreshSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = self.auth_service.refresh_token(
            serializer.validated_data
        )

        return ApiResponse.success(
            message=Messages.TOKEN_REFRESHED,
            data=data,
            status_code=StatusCode.OK
        )
