from rest_framework import serializers


class SecurityPasswordSerializer(serializers.Serializer):

    password = serializers.CharField()
