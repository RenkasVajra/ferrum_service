from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from rest_framework import permissions, serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import OTPRequest

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class ConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)

    def validate(self, attrs):
        email = attrs["email"]
        code = attrs["code"]

        try:
            otp = OTPRequest.objects.get(email=email)
        except OTPRequest.DoesNotExist as exc:
            raise serializers.ValidationError({"email": "Код для этого email не найден."}) from exc

        if otp.is_expired():
            raise serializers.ValidationError({"code": "Срок действия кода истек."})

        if otp.code != code:
            otp.register_attempt(False)
            raise serializers.ValidationError({"code": "Неверный код подтверждения."})

        attrs["otp"] = otp
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "is_staff"]
        read_only_fields = fields


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        otp = OTPRequest.issue_code(email=email)

        send_mail(
            subject="Ваш код авторизации",
            message=f"Ваш одноразовый код: {otp.code}",
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, "DEFAULT_FROM_EMAIL") else None,
            recipient_list=[email],
            fail_silently=True,
        )

        return Response(
            {"detail": "Код отправлен на указанный email."},
            status=status.HTTP_200_OK,
        )


class ConfirmView(APIView):
    permission_classes = (permissions.AllowAny,)

    @transaction.atomic
    def post(self, request: Request) -> Response:
        serializer = ConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp: OTPRequest = serializer.validated_data["otp"]
        email = serializer.validated_data["email"]

        user, _created = User.objects.get_or_create(
            email=email,
            defaults={"username": email},
        )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        otp.delete()

        response = Response(
            {
                "access": access_token,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            settings.OTP_COOKIE_NAME,
            str(refresh),
            max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
            secure=settings.OTP_COOKIE_SECURE,
            httponly=True,
            samesite="Lax",
        )
        return response


