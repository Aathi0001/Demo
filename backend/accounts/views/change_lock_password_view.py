from rest_framework.views import APIView

from accounts.serializers.security_change_password_serializer import SecurityChangePasswordSerializer
from accounts.services.auth_service import AuthService

from common.responses import ApiResponse
from common.messages import Messages


class ChangeLockPasswordView(APIView):

    auth_service = AuthService()

    def put(self, request):

        serializer = SecurityChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        success = self.auth_service.change_lock_password(
            request.user,
            serializer.validated_data["old_password"],
            serializer.validated_data["new_password"]
        )

        if not success:
            return ApiResponse.error(
                message=Messages.INVALID_LOCK_PASSWORD
            )

        return ApiResponse.success(
            message=Messages.LOCK_PASSWORD_CHANGED
        )
