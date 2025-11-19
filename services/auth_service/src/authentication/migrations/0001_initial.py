from django.db import migrations, models

import authentication.models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="OTPRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("code", models.CharField(help_text="Одноразовый шестизначный код подтверждения.", max_length=6)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField(default=authentication.models.default_expiration)),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("last_sent_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ("-created_at",),
                "verbose_name": "OTP запрос",
                "verbose_name_plural": "OTP запросы",
            },
        ),
    ]

