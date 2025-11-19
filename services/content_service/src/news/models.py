from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class NewsArticle(models.Model):
    """Основная сущность новости/обновления платформы."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        PUBLISHED = "published", "Опубликовано"
        ARCHIVED = "archived", "В архиве"

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    summary = models.CharField(max_length=512, blank=True)
    body = models.TextField()
    cover_image = models.URLField(blank=True)
    author_name = models.CharField(max_length=128, default="Команда Ferrum")
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField(blank=True, null=True)
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.CharField(max_length=512, blank=True)
    tags = models.JSONField(default=list, blank=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-published_at", "-created_at")
        verbose_name = "Новость"
        verbose_name_plural = "Новости"

    def publish(self) -> None:
        if self.status != self.Status.PUBLISHED:
            self.status = self.Status.PUBLISHED
        if not self.published_at:
            self.published_at = timezone.now()

    def save(self, *args, **kwargs):
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self) -> str:  # pragma: no cover
        return self.title


class NewsChangelog(models.Model):
    """Изменения по выпуску/фиче внутри новости."""

    article = models.ForeignKey(NewsArticle, related_name="changelog", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    impact_area = models.CharField(max_length=128, help_text="Например: 'Админка', 'Бекенд', 'Инфраструктура'.")
    change_type = models.CharField(
        max_length=64,
        choices=[
            ("added", "Добавлено"),
            ("changed", "Изменено"),
            ("fixed", "Исправлено"),
            ("removed", "Удалено"),
        ],
    )
    metadata = models.JSONField(blank=True, default=dict)

    class Meta:
        ordering = ("id",)
        verbose_name = "Запись changelog"
        verbose_name_plural = "Changelog записи"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.article.title}: {self.title}"


class NewsEvent(models.Model):
    """Лог передачи события о публикации в внешние системы через Redis Streams."""

    article = models.ForeignKey(NewsArticle, related_name="events", on_delete=models.CASCADE)
    stream_id = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    payload = models.JSONField()

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Событие новости"
        verbose_name_plural = "События новостей"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.stream_id} -> {self.article_id}"


