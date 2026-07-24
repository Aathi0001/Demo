from rest_framework.views import APIView

from accounts.services.auth_service import AuthService

from common.responses import ApiResponse
from common.messages import Messages


class ForgotDeletePasswordView(APIView):

    auth_service = AuthService()

    def post(self, request):

        success = self.auth_service.forgot_delete_password(
            request.user
        )

        if not success:
            return ApiResponse.error(
                message=Messages.PASSWORD_RESET_ALREADY_SCHEDULED
            )

        return ApiResponse.success(
            message=Messages.DELETE_PASSWORD_RESET_SCHEDULED
        )
