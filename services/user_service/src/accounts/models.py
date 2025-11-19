from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "admin", "Администратор"
        MANAGER = "manager", "Менеджер"
        CUSTOMER = "customer", "Клиент"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=32, choices=Roles.choices, default=Roles.CUSTOMER)
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.email} ({self.get_role_display()})"

