from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion


def default_schema():
    return {
        "sections": [],
        "props": {},
    }


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PageTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=128)),
                ("slug", models.SlugField(max_length=128, unique=True)),
                ("description", models.TextField(blank=True)),
                ("schema", models.JSONField(default=default_schema)),
                ("preview_image", models.URLField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Шаблон страницы",
                "verbose_name_plural": "Шаблоны страниц",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Page",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=150, unique=True)),
                ("locale", models.CharField(default="ru", max_length=10)),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Черновик"), ("review", "На проверке"), ("published", "Опубликована")],
                        default="draft",
                        max_length=32,
                    ),
                ),
                ("blocks", models.JSONField(default=default_schema)),
                ("seo_title", models.CharField(blank=True, max_length=255)),
                ("seo_description", models.CharField(blank=True, max_length=512)),
                ("seo_keywords", models.CharField(blank=True, max_length=512)),
                ("publish_at", models.DateTimeField(blank=True, null=True)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("created_by", models.CharField(blank=True, max_length=128)),
                ("updated_by", models.CharField(blank=True, max_length=128)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "template",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="pages",
                        to="pages.pagetemplate",
                    ),
                ),
            ],
            options={
                "verbose_name": "Страница",
                "verbose_name_plural": "Страницы",
                "ordering": ("slug",),
            },
        ),
        migrations.CreateModel(
            name="PageEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("stream_id", models.CharField(max_length=128)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("payload", models.JSONField()),
                (
                    "page",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="pages.page"),
                ),
            ],
            options={
                "verbose_name": "Событие страницы",
                "verbose_name_plural": "События страниц",
                "ordering": ("-created_at",),
            },
        ),
    ]


