from __future__ import annotations

from rest_framework import filters, response, serializers, status, viewsets

from catalog.models import Category
from common.permissions import IsAdminOrReadOnly


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "parent",
            "is_active",
            "position",
            "icon",
            "meta",
            "children",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("created_at", "updated_at")

    def get_children(self, obj):
        if not self.context.get("include_children"):
            return None
        serializer = CategorySerializer(
            obj.children.all().order_by("position", "name"), many=True, context=self.context
        )
        return serializer.data


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("position", "name")
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("name", "slug")
    ordering_fields = ("position", "created_at")

    def list(self, request, *args, **kwargs):
        if request.query_params.get("tree") == "true":
            roots = self.get_queryset().filter(parent__isnull=True)
            serializer = self.get_serializer(
                roots,
                many=True,
                context={**self.get_serializer_context(), "include_children": True},
            )
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return super().list(request, *args, **kwargs)


