from rest_framework.views import APIView

from accounts.serializers.change_password_serializer import ChangePasswordSerializer
from accounts.services.auth_service import AuthService

from common.messages import Messages
from common.responses import ApiResponse


class ChangePasswordView(APIView):

    auth_service = AuthService()

    def put(self, request):

        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        success = self.auth_service.change_login_password(
            request.user,
            serializer.validated_data
        )

        if not success:
            return ApiResponse.error(
                message=Messages.INVALID_PASSWORD
            )

        return ApiResponse.success(
            message=Messages.LOGIN_PASSWORD_CHANGED
        )
