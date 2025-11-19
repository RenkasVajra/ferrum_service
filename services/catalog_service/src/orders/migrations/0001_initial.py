from __future__ import annotations

from decimal import Decimal

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("goods", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeliveryMethod",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("code", models.SlugField(max_length=64, unique=True)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("min_days", models.PositiveIntegerField(default=1)),
                ("max_days", models.PositiveIntegerField(default=5)),
                ("base_price", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10)),
                ("price_per_kg", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10)),
                ("logo", models.ImageField(blank=True, null=True, upload_to="delivery-methods/")),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Метод доставки",
                "verbose_name_plural": "Методы доставки",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="PaymentMethod",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("code", models.SlugField(max_length=64, unique=True)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("provider", models.CharField(default="yookassa", max_length=64)),
                ("logo", models.ImageField(blank=True, null=True, upload_to="payment-methods/")),
                ("fee_percent", models.DecimalField(decimal_places=2, default=Decimal("0.0"), max_digits=5)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Метод оплаты",
                "verbose_name_plural": "Методы оплаты",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Checkout",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_id", models.PositiveBigIntegerField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Черновик"),
                            ("pending", "Ожидание оплаты"),
                            ("paid", "Оплачено"),
                            ("failed", "Ошибка"),
                            ("cancelled", "Отменено"),
                        ],
                        default="draft",
                        max_length=32,
                    ),
                ),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("currency", models.CharField(default="RUB", max_length=3)),
                ("delivery_price", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10)),
                ("payment_fee", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10)),
                ("items_snapshot", models.JSONField(default=list)),
                ("recipient_data", models.JSONField(default=dict)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "delivery_method",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="orders.deliverymethod"),
                ),
                (
                    "payment_method",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="orders.paymentmethod"),
                ),
            ],
            options={
                "verbose_name": "Чекаут",
                "verbose_name_plural": "Чекауты",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="BasketItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_id", models.PositiveBigIntegerField()),
                ("count", models.PositiveIntegerField(default=1)),
                ("price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("currency", models.CharField(default="RUB", max_length=3)),
                ("variant_key", models.CharField(blank=True, max_length=128)),
                ("variant_data", models.JSONField(blank=True, default=dict)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "product",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="basket_items", to="goods.product"),
                ),
            ],
            options={
                "verbose_name": "Элемент корзины",
                "verbose_name_plural": "Элементы корзины",
            },
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(default="yookassa", max_length=64)),
                ("external_id", models.CharField(max_length=128, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("initiated", "Инициирована"), ("succeeded", "Успешна"), ("failed", "Ошибочна")],
                        default="initiated",
                        max_length=32,
                    ),
                ),
                ("payload", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "checkout",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="transactions", to="orders.checkout"),
                ),
            ],
            options={
                "verbose_name": "Транзакция",
                "verbose_name_plural": "Транзакции",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="CheckoutItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("sku", models.CharField(max_length=64)),
                ("price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("currency", models.CharField(default="RUB", max_length=3)),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                (
                    "checkout",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="orders.checkout"),
                ),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="goods.product")),
            ],
            options={
                "verbose_name": "Позиция чекаута",
                "verbose_name_plural": "Позиции чекаута",
            },
        ),
        migrations.AddConstraint(
            model_name="basketitem",
            constraint=models.UniqueConstraint(
                fields=("user_id", "product", "variant_key"), name="unique_basket_item_per_variant"
            ),
        ),
    ]


