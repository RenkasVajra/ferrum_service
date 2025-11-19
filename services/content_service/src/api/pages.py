from __future__ import annotations

import logging

from django.conf import settings
from django_redis import get_redis_connection
from rest_framework import filters, mixins, permissions, serializers, viewsets

from pages.models import Page, PageEvent, PageTemplate

logger = logging.getLogger(__name__)


class PageTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageTemplate
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "schema",
            "preview_image",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("created_at", "updated_at")


class PageSerializer(serializers.ModelSerializer):
    template = PageTemplateSerializer(read_only=True)
    template_id = serializers.PrimaryKeyRelatedField(
        queryset=PageTemplate.objects.all(), source="template", write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Page
        fields = [
            "id",
            "title",
            "slug",
            "locale",
            "status",
            "blocks",
            "seo_title",
            "seo_description",
            "seo_keywords",
            "publish_at",
            "published_at",
            "template",
            "template_id",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("published_at", "created_at", "updated_at")


class PublishedPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = [
            "id",
            "title",
            "slug",
            "locale",
            "blocks",
            "seo_title",
            "seo_description",
            "seo_keywords",
            "published_at",
        ]


def publish_page_event(page: Page) -> None:
    stream = getattr(settings, "PAGE_STREAM", None)
    if not stream:
        return
    payload = {
        "page_id": str(page.id),
        "slug": page.slug,
        "locale": page.locale,
        "published_at": page.published_at.isoformat() if page.published_at else "",
    }
    try:
        conn = get_redis_connection("default")
        stream_id = conn.xadd(stream, payload)
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to push page event to redis: %s", exc)
        stream_id = "offline"
    PageEvent.objects.create(page=page, stream_id=stream_id, payload=payload)


class PageTemplateViewSet(viewsets.ModelViewSet):
    queryset = PageTemplate.objects.all()
    serializer_class = PageTemplateSerializer
    permission_classes = (permissions.IsAdminUser,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("name", "description")
    ordering_fields = ("name", "created_at")


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.select_related("template").all()
    serializer_class = PageSerializer
    permission_classes = (permissions.IsAdminUser,)
    lookup_value_regex = "[0-9]+"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("title", "slug")
    ordering_fields = ("created_at", "updated_at")

    def perform_create(self, serializer):
        page = serializer.save()
        if page.status == Page.Status.PUBLISHED:
            publish_page_event(page)

    def perform_update(self, serializer):
        page = serializer.save()
        if page.status == Page.Status.PUBLISHED:
            publish_page_event(page)


class PublishedPageViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PublishedPageSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = "slug"
    queryset = Page.objects.filter(status=Page.Status.PUBLISHED)

    def get_queryset(self):
        return (
            Page.objects.filter(status=Page.Status.PUBLISHED)
            .only("id", "slug", "title", "locale", "blocks", "seo_title", "seo_description", "seo_keywords", "published_at")
            .order_by("slug")
        )


