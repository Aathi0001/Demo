from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField( write_only=True )

    class Meta:
        model = User
        fields = ( "username", "email", "password", "confirm_password", )

        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }

    def validate_username(self, value):

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError( "Username already exists." )

        return value

    def validate_email(self, value):

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError( "Email already exists." )

        return value

    def validate(self, attrs):

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {
                    "confirm_password": "Passwords do not match."
                }
            )

        return attrs
