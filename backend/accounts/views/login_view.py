from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from accounts.serializers.login_serializer import LoginSerializer
from accounts.services.auth_service import AuthService
from common.messages import Messages
from common.responses import ApiResponse
from common.status_codes import StatusCode


class LoginView(APIView):

    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = AuthService()

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = self.auth_service.login(
            serializer.validated_data
        )

        return ApiResponse.success(
            message=Messages.LOGIN_SUCCESS,
            data=data,
            status_code=StatusCode.OK,
        )
