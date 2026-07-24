from rest_framework.views import APIView

from accounts.serializers.profile_serializer import ProfileSerializer
from accounts.services.auth_service import AuthService
from common.messages import Messages
from common.responses import ApiResponse


class ProfileView(APIView):

    auth_service = AuthService()

    def get(self, request):

        profile = self.auth_service.get_profile(
            request.user
        )

        serializer = ProfileSerializer(profile)

        return ApiResponse.success(
            message=Messages.PROFILE_FETCHED,
            data=serializer.data
        )

    def put(self, request):

        profile = self.auth_service.get_profile(
            request.user
        )

        serializer = ProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        profile = self.auth_service.update_profile(
            request.user,
            serializer.validated_data
        )

        return ApiResponse.success(
            message=Messages.PROFILE_UPDATED,
            data=ProfileSerializer(profile).data
        )
