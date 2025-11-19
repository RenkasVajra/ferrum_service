from __future__ import annotations

import logging

from django.conf import settings
from django_redis import get_redis_connection
from rest_framework import filters, mixins, permissions, serializers, viewsets

from news.models import NewsArticle, NewsChangelog, NewsEvent

logger = logging.getLogger(__name__)


class NewsChangelogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsChangelog
        fields = ["id", "title", "description", "impact_area", "change_type", "metadata"]


class NewsArticleSerializer(serializers.ModelSerializer):
    changelog = NewsChangelogSerializer(many=True, required=False)

    class Meta:
        model = NewsArticle
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "body",
            "cover_image",
            "author_name",
            "status",
            "published_at",
            "seo_title",
            "seo_description",
            "tags",
            "featured",
            "changelog",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("created_at", "updated_at")

    def create(self, validated_data):
        changelog_data = validated_data.pop("changelog", [])
        article = super().create(validated_data)
        self._sync_changelog(article, changelog_data)
        return article

    def update(self, instance, validated_data):
        changelog_data = validated_data.pop("changelog", None)
        article = super().update(instance, validated_data)
        if changelog_data is not None:
            article.changelog.all().delete()
            self._sync_changelog(article, changelog_data)
        return article

    def _sync_changelog(self, article: NewsArticle, changelog_data):
        for entry in changelog_data:
            NewsChangelog.objects.create(article=article, **entry)


class PublicNewsSerializer(serializers.ModelSerializer):
    changelog = NewsChangelogSerializer(many=True, read_only=True)

    class Meta:
        model = NewsArticle
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "body",
            "cover_image",
            "author_name",
            "published_at",
            "seo_title",
            "seo_description",
            "tags",
            "featured",
            "changelog",
        ]


def publish_news_event(article: NewsArticle) -> None:
    """Push publication event into Redis Streams for other services."""
    stream = getattr(settings, "NEWS_STREAM", None)
    if not stream:
        return
    payload = {
        "article_id": str(article.id),
        "slug": article.slug,
        "title": article.title,
        "summary": article.summary,
        "published_at": article.published_at.isoformat() if article.published_at else "",
        "tags": ",".join(article.tags or []),
    }
    try:
        conn = get_redis_connection("default")
        stream_id = conn.xadd(stream, payload)
    except Exception as exc:  # pragma: no cover - network errors
        logger.warning("Failed to push news event to redis: %s", exc)
        stream_id = "offline"
    NewsEvent.objects.create(article=article, stream_id=stream_id, payload=payload)


class NewsViewSet(viewsets.ModelViewSet):
    """Административный CRUD по новостям и changelog."""

    queryset = NewsArticle.objects.prefetch_related("changelog").all()
    serializer_class = NewsArticleSerializer
    permission_classes = (permissions.IsAdminUser,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("title", "summary", "tags")
    ordering_fields = ("published_at", "created_at")

    def perform_create(self, serializer):
        article = serializer.save()
        if article.status == NewsArticle.Status.PUBLISHED:
            publish_news_event(article)

    def perform_update(self, serializer):
        article = serializer.save()
        if article.status == NewsArticle.Status.PUBLISHED:
            publish_news_event(article)


class PublicNewsViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Публичный API списка новостей для клиентского фронтенда."""

    serializer_class = PublicNewsSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("title", "summary", "tags")
    ordering_fields = ("published_at",)

    def get_queryset(self):
        return (
            NewsArticle.objects.filter(status=NewsArticle.Status.PUBLISHED)
            .prefetch_related("changelog")
            .order_by("-published_at")
        )


