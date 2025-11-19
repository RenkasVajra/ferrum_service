from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import filters, permissions, serializers, viewsets

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "is_staff",
            "is_email_verified",
            "password",
        ]
        read_only_fields = ("is_staff", "is_email_verified")

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserViewSet(viewsets.ModelViewSet):
    """CRUD операции для пользователей (административный доступ)."""

    serializer_class = UserSerializer
    queryset = User.objects.all().order_by("-date_joined")
    permission_classes = (permissions.IsAdminUser,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("email", "first_name", "last_name")
    ordering_fields = ("date_joined", "email")


