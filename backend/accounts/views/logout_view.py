from rest_framework.views import APIView

from accounts.serializers.refresh_serializer import RefreshSerializer
from accounts.services.auth_service import AuthService

from common.responses import ApiResponse
from common.messages import Messages


class LogoutView(APIView):

    auth_service = AuthService()

    def post(self, request):

        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.auth_service.logout(serializer.validated_data)

        return ApiResponse.success(
            message=Messages.LOGOUT_SUCCESS
        )
