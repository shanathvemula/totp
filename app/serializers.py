from rest_framework import serializers


class OTPVerifySerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    otp = serializers.CharField()
