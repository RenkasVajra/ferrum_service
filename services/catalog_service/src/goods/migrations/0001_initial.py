from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Brand",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("country", models.CharField(blank=True, max_length=128)),
                ("website", models.URLField(blank=True)),
                ("logo", models.ImageField(blank=True, null=True, upload_to="brands/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Бренд",
                "verbose_name_plural": "Бренды",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Size",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=64)),
                ("code", models.CharField(max_length=32)),
                (
                    "size_type",
                    models.CharField(
                        choices=[
                            ("clothes", "Одежда"),
                            ("shoes", "Обувь"),
                            ("accessory", "Аксессуары"),
                            ("universal", "Универсальный"),
                        ],
                        default="universal",
                        max_length=32,
                    ),
                ),
                ("description", models.CharField(blank=True, max_length=255)),
                ("measurements", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "verbose_name": "Размер",
                "verbose_name_plural": "Размеры",
                "ordering": ("size_type", "name"),
                "unique_together": {("code", "size_type")},
            },
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("sku", models.CharField(max_length=64, unique=True)),
                ("price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("currency", models.CharField(default="RUB", max_length=3)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("in_stock", "В наличии"),
                            ("out_of_stock", "Нет в наличии"),
                            ("preorder", "Предзаказ"),
                        ],
                        default="in_stock",
                        max_length=32,
                    ),
                ),
                ("is_published", models.BooleanField(default=False)),
                ("attributes", models.JSONField(blank=True, default=dict)),
                ("meta", models.JSONField(blank=True, default=dict)),
                ("stock", models.PositiveIntegerField(default=0)),
                ("weight_grams", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "brand",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="products", to="goods.brand"),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="products", to="catalog.category"
                    ),
                ),
            ],
            options={
                "verbose_name": "Товар",
                "verbose_name_plural": "Товары",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="ProductImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to="products/")),
                ("alt_text", models.CharField(blank=True, max_length=255)),
                ("position", models.PositiveIntegerField(default=0)),
                (
                    "product",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="images", to="goods.product"),
                ),
            ],
            options={
                "verbose_name": "Изображение товара",
                "verbose_name_plural": "Изображения товаров",
                "ordering": ("position", "id"),
            },
        ),
        migrations.CreateModel(
            name="ProductSize",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("price_modifier", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10)),
                ("stock", models.PositiveIntegerField(default=0)),
                (
                    "product",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="goods.product"),
                ),
                (
                    "size",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="goods.size"),
                ),
            ],
            options={
                "verbose_name": "Размер товара",
                "verbose_name_plural": "Размеры товара",
                "unique_together": {("product", "size")},
            },
        ),
        migrations.AddField(
            model_name="product",
            name="sizes",
            field=models.ManyToManyField(blank=True, related_name="products", through="goods.ProductSize", to="goods.size"),
        ),
    ]


