from __future__ import annotations

from django.db import models
from django.utils import timezone


def default_schema():
    return {
        "sections": [],
        "props": {},
    }


class PageTemplate(models.Model):
    """Reusable template to bootstrap landing pages in the builder."""

    name = models.CharField(max_length=128)
    slug = models.SlugField(unique=True, max_length=128)
    description = models.TextField(blank=True)
    schema = models.JSONField(default=default_schema)
    preview_image = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Шаблон страницы"
        verbose_name_plural = "Шаблоны страниц"

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Page(models.Model):
    """Concrete page that will be rendered on the client Next.js app."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        REVIEW = "review", "На проверке"
        PUBLISHED = "published", "Опубликована"

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=150)
    locale = models.CharField(max_length=10, default="ru")
    template = models.ForeignKey(PageTemplate, null=True, blank=True, on_delete=models.SET_NULL, related_name="pages")
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.DRAFT)
    blocks = models.JSONField(default=default_schema)
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.CharField(max_length=512, blank=True)
    seo_keywords = models.CharField(max_length=512, blank=True)
    publish_at = models.DateTimeField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=128, blank=True)
    updated_by = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("slug",)
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"

    def save(self, *args, **kwargs):
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self) -> str:  # pragma: no cover
        return self.slug


class PageEvent(models.Model):
    page = models.ForeignKey(Page, related_name="events", on_delete=models.CASCADE)
    stream_id = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    payload = models.JSONField()

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Событие страницы"
        verbose_name_plural = "События страниц"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.page.slug} -> {self.stream_id}"


