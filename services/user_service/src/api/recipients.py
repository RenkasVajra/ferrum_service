from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import filters, permissions, serializers, viewsets

from recipients.models import Recipient

User = get_user_model()


class RecipientSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Recipient
        fields = [
            "id",
            "user",
            "user_email",
            "full_name",
            "phone",
            "country",
            "city",
            "postal_code",
            "address_line1",
            "address_line2",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("created_at", "updated_at", "user_email")


class MyRecipientSerializer(RecipientSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())


class RecipientViewSet(viewsets.ModelViewSet):
    """Admin CRUD for managing all recipients."""

    queryset = Recipient.objects.select_related("user").all()
    serializer_class = RecipientSerializer
    permission_classes = (permissions.IsAdminUser,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("full_name", "city", "user__email")
    ordering_fields = ("created_at", "city")


class MyRecipientViewSet(viewsets.ModelViewSet):
    """Customer-facing CRUD limited to own recipients."""

    serializer_class = MyRecipientSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("full_name", "city")
    ordering_fields = ("created_at",)

    def get_queryset(self):
        return Recipient.objects.filter(user=self.request.user)


