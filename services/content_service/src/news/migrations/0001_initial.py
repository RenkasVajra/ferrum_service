from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="NewsArticle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255, unique=True)),
                ("summary", models.CharField(blank=True, max_length=512)),
                ("body", models.TextField()),
                ("cover_image", models.URLField(blank=True)),
                ("author_name", models.CharField(default="Команда Ferrum", max_length=128)),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Черновик"), ("published", "Опубликовано"), ("archived", "В архиве")],
                        default="draft",
                        max_length=32,
                    ),
                ),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("seo_title", models.CharField(blank=True, max_length=255)),
                ("seo_description", models.CharField(blank=True, max_length=512)),
                ("tags", models.JSONField(blank=True, default=list)),
                ("featured", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Новость",
                "verbose_name_plural": "Новости",
                "ordering": ("-published_at", "-created_at"),
            },
        ),
        migrations.CreateModel(
            name="NewsChangelog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("impact_area", models.CharField(help_text="Например: 'Админка', 'Бекенд', 'Инфраструктура'.", max_length=128)),
                (
                    "change_type",
                    models.CharField(
                        choices=[
                            ("added", "Добавлено"),
                            ("changed", "Изменено"),
                            ("fixed", "Исправлено"),
                            ("removed", "Удалено"),
                        ],
                        max_length=64,
                    ),
                ),
                ("metadata", models.JSONField(blank=True, default=dict)),
                (
                    "article",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="changelog", to="news.newsarticle"),
                ),
            ],
            options={
                "verbose_name": "Запись changelog",
                "verbose_name_plural": "Changelog записи",
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="NewsEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("stream_id", models.CharField(max_length=128)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("payload", models.JSONField()),
                (
                    "article",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="news.newsarticle"),
                ),
            ],
            options={
                "verbose_name": "Событие новости",
                "verbose_name_plural": "События новостей",
                "ordering": ("-created_at",),
            },
        ),
    ]


