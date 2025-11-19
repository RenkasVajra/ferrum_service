from __future__ import annotations

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Recipient",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=255)),
                ("phone", models.CharField(blank=True, max_length=32)),
                ("country", models.CharField(default="Россия", max_length=128)),
                ("city", models.CharField(max_length=128)),
                ("postal_code", models.CharField(blank=True, max_length=32)),
                ("address_line1", models.CharField(max_length=255)),
                ("address_line2", models.CharField(blank=True, max_length=255)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recipients",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Получатель",
                "verbose_name_plural": "Получатели",
                "ordering": ("-created_at",),
            },
        ),
        migrations.AddConstraint(
            model_name="recipient",
            constraint=models.UniqueConstraint(
                fields=("user", "full_name", "address_line1"),
                name="unique_recipient_per_user",
            ),
        ),
    ]


