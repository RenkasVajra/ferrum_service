from __future__ import annotations

import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone

User = get_user_model()


def default_expiration() -> timezone.datetime:
    return timezone.now() + timedelta(minutes=5)


class OTPRequest(models.Model):
    email = models.EmailField(unique=True)
    code = models.CharField(
        max_length=6,
        validators=[MinLengthValidator(6)],
        help_text="Одноразовый шестизначный код подтверждения.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiration)
    attempts = models.PositiveSmallIntegerField(default=0)
    last_sent_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "OTP запрос"
        verbose_name_plural = "OTP запросы"

    @classmethod
    def issue_code(cls, email: str) -> "OTPRequest":
        code = "".join(secrets.choice("0123456789") for _ in range(6))
        obj, _created = cls.objects.update_or_create(
            email=email,
            defaults={
                "code": code,
                "expires_at": timezone.now() + timedelta(minutes=5),
                "attempts": 0,
            },
        )
        return obj

    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    def register_attempt(self, success: bool) -> None:
        self.attempts = models.F("attempts") + 1
        self.save(update_fields=["attempts"])
        if not success and self.attempts >= getattr(settings, "OTP_MAX_ATTEMPTS", 5):
            self.expires_at = timezone.now()
            self.save(update_fields=["expires_at"])

    def __str__(self) -> str:  # pragma: no cover - human readable
        return f"OTPRequest(email={self.email}, expires_at={self.expires_at})"

