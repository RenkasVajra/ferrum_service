from __future__ import annotations

from django.conf import settings
from django.db import models


class Recipient(models.Model):
    """Represents a shipping recipient for a specific user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipients",
    )
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32, blank=True)
    country = models.CharField(max_length=128, default="Россия")
    city = models.CharField(max_length=128)
    postal_code = models.CharField(max_length=32, blank=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "full_name", "address_line1"],
                name="unique_recipient_per_user",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.full_name} ({self.city})"


