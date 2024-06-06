from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp import devices_for_user

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

import qrcode
import qrcode.image.svg
import cv2
import base64

from app.serializers import OTPVerifySerializer


# Create your views here.

class TOTPSetupView(APIView):

    def post(self, request, *args, **kwargs):
        data = request.data
        user = authenticate(username=data['username'], password=data['password'])
        # print(user.device_img)
        if user:
            if user.is_active:
                device, created = TOTPDevice.objects.get_or_create(user=user, name='default')

                if created:
                    device.save()

                provisioning_uri = device.config_url
                img = qrcode.make(provisioning_uri, image_factory=qrcode.image.svg.SvgImage)
                img.save('img.svg')
                with open("img.svg", "rb") as img_file:
                    # print(img_file.read())
                    my_string = base64.b64encode(img_file.read())
                my_string = my_string.decode('utf-8')
                user.device_img = my_string
                user.provisioning_uri = provisioning_uri
                user.save()
                # user.objects.

                return Response({"image": my_string}, status=status.HTTP_200_OK)
            else:
                return Response({"Error": "Invalid User"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        else:
            return Response({"Error": "Invalid credentials"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class OTPVerifyView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            otp = serializer.validated_data['otp']

            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    return Response({"error": "User account is disabled."}, status=status.HTTP_403_FORBIDDEN)

                device = next(devices_for_user(user, confirmed=True), None)
                if device and device.verify_token(otp):
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)