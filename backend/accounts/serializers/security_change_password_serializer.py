from rest_framework import serializers

from common.messages import Messages


class SecurityChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField()

    new_password = serializers.CharField()

    confirm_password = serializers.CharField()

    def validate(self, attrs):

        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {
                    "confirm_password": Messages.PASSWORDS_DO_NOT_MATCH
                }
            )

        return attrs
