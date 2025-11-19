from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from goods.models import Product


class PaymentMethod(models.Model):
    name = models.CharField(max_length=255)
    code = models.SlugField(unique=True, max_length=64)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    provider = models.CharField(max_length=64, default="yookassa")
    logo = models.ImageField(upload_to="payment-methods/", blank=True, null=True)
    fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.0"))
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Метод оплаты"
        verbose_name_plural = "Методы оплаты"

    def __str__(self):  # pragma: no cover
        return self.name


class DeliveryMethod(models.Model):
    name = models.CharField(max_length=255)
    code = models.SlugField(unique=True, max_length=64)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    min_days = models.PositiveIntegerField(default=1)
    max_days = models.PositiveIntegerField(default=5)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    logo = models.ImageField(upload_to="delivery-methods/", blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Метод доставки"
        verbose_name_plural = "Методы доставки"

    def __str__(self):  # pragma: no cover
        return self.name


class BasketItem(models.Model):
    user_id = models.PositiveBigIntegerField()
    product = models.ForeignKey(Product, related_name="basket_items", on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="RUB")
    variant_key = models.CharField(max_length=128, blank=True)
    variant_data = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user_id", "product", "variant_key"],
                name="unique_basket_item_per_variant",
            )
        ]
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"

    def __str__(self):  # pragma: no cover
        return f"{self.user_id} -> {self.product}"


class Checkout(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        PENDING = "pending", "Ожидание оплаты"
        PAID = "paid", "Оплачено"
        FAILED = "failed", "Ошибка"
        CANCELLED = "cancelled", "Отменено"

    user_id = models.PositiveBigIntegerField()
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    delivery_method = models.ForeignKey(DeliveryMethod, on_delete=models.PROTECT)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.DRAFT)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="RUB")
    delivery_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    payment_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    items_snapshot = models.JSONField(default=list)
    recipient_data = models.JSONField(default=dict)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Чекаут"
        verbose_name_plural = "Чекауты"

    def __str__(self):  # pragma: no cover
        return f"Checkout #{self.id}"


class CheckoutItem(models.Model):
    checkout = models.ForeignKey(Checkout, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="RUB")
    quantity = models.PositiveIntegerField(default=1)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Позиция чекаута"
        verbose_name_plural = "Позиции чекаута"


class Transaction(models.Model):
    class Status(models.TextChoices):
        INITIATED = "initiated", "Инициирована"
        SUCCEEDED = "succeeded", "Успешна"
        FAILED = "failed", "Ошибочна"

    checkout = models.ForeignKey(Checkout, related_name="transactions", on_delete=models.CASCADE)
    provider = models.CharField(max_length=64, default="yookassa")
    external_id = models.CharField(max_length=128, unique=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.INITIATED)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"


