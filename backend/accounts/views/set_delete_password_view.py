from rest_framework.views import APIView

from accounts.serializers.security_password_serializer import SecurityPasswordSerializer
from accounts.services.auth_service import AuthService

from common.responses import ApiResponse
from common.messages import Messages


class SetDeletePasswordView(APIView):

    auth_service = AuthService()

    def post(self, request):

        serializer = SecurityPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        success = self.auth_service.set_delete_password(
            request.user,
            serializer.validated_data["password"]
        )

        if not success:
            return ApiResponse.error(
                message=Messages.PASSWORD_ALREADY_SET
            )

        return ApiResponse.success(
            message=Messages.DELETE_PASSWORD_SET
        )
