from django.urls import path
from .views import TOTPSetupView, OTPVerifyView

urlpatterns = [
    path('totp-setup/', TOTPSetupView.as_view(), name='totp-setup'),
    path('token/', OTPVerifyView.as_view(), name='Token')
]
