from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.responses import ApiResponse
from common.messages import Messages
from common.status_codes import StatusCode

from accounts.serializers.register_serializer import RegisterSerializer
from accounts.services.auth_service import AuthService


class RegisterView(APIView):

    authentication_classes = []

    permission_classes = []

    def post(self, request):

        serializer = RegisterSerializer( data=request.data )

        serializer.is_valid( raise_exception=True )

        AuthService.register( serializer.validated_data )

        return ApiResponse.success(
            message=Messages.USER_REGISTERED,
            status_code=StatusCode.CREATED
        )
