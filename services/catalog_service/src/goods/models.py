from __future__ import annotations

from decimal import Decimal

from django.db import models

from catalog.models import Category


class Brand(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField(blank=True)
    country = models.CharField(max_length=128, blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Size(models.Model):
    class SizeType(models.TextChoices):
        CLOTHES = "clothes", "Одежда"
        SHOES = "shoes", "Обувь"
        ACCESSORY = "accessory", "Аксессуары"
        UNIVERSAL = "universal", "Универсальный"

    name = models.CharField(max_length=64)
    code = models.CharField(max_length=32)
    size_type = models.CharField(max_length=32, choices=SizeType.choices, default=SizeType.UNIVERSAL)
    description = models.CharField(max_length=255, blank=True)
    measurements = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("size_type", "name")
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"
        unique_together = ("code", "size_type")

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} ({self.code})"


class Product(models.Model):
    class Availability(models.TextChoices):
        IN_STOCK = "in_stock", "В наличии"
        OUT_OF_STOCK = "out_of_stock", "Нет в наличии"
        PREORDER = "preorder", "Предзаказ"

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, related_name="products", on_delete=models.PROTECT)
    brand = models.ForeignKey(Brand, related_name="products", on_delete=models.PROTECT)
    sku = models.CharField(max_length=64, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="RUB")
    status = models.CharField(max_length=32, choices=Availability.choices, default=Availability.IN_STOCK)
    is_published = models.BooleanField(default=False)
    attributes = models.JSONField(default=dict, blank=True)
    meta = models.JSONField(default=dict, blank=True)
    stock = models.PositiveIntegerField(default=0)
    weight_grams = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sizes = models.ManyToManyField(Size, through="ProductSize", blank=True, related_name="products")

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    price_modifier = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("product", "size")
        verbose_name = "Размер товара"
        verbose_name_plural = "Размеры товара"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=255, blank=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("position", "id")
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"


