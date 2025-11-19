from __future__ import annotations

from decimal import Decimal
from typing import List

from django.conf import settings
from django.db import transaction
from rest_framework import filters, permissions, serializers, viewsets

from common.permissions import IsAdminOrReadOnly
from goods.models import Product
from orders.models import (
    BasketItem,
    Checkout,
    CheckoutItem,
    DeliveryMethod,
    PaymentMethod,
    Transaction,
)
from orders.payments import create_payment
from orders.services import publish_checkout_event


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = [
            "id",
            "name",
            "code",
            "description",
            "is_active",
            "provider",
            "logo",
            "fee_percent",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("created_at", "updated_at")


class DeliveryMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryMethod
        fields = [
            "id",
            "name",
            "code",
            "description",
            "is_active",
            "min_days",
            "max_days",
            "base_price",
            "price_per_kg",
            "logo",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("created_at", "updated_at")


class BasketItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.DecimalField(source="product.price", max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = BasketItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_price",
            "count",
            "price",
            "currency",
            "variant_key",
            "variant_data",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("price", "currency", "created_at", "updated_at")

    def validate_count(self, value):
        if value <= 0:
            raise serializers.ValidationError("Количество должно быть больше нуля.")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user_id"] = user.id
        product: Product = validated_data["product"]
        validated_data["price"] = product.price
        validated_data["currency"] = product.currency
        instance, _created = BasketItem.objects.update_or_create(
            user_id=user.id,
            product=product,
            variant_key=validated_data.get("variant_key", ""),
            defaults=validated_data,
        )
        return instance

    def update(self, instance, validated_data):
        instance.count = validated_data.get("count", instance.count)
        instance.variant_data = validated_data.get("variant_data", instance.variant_data)
        instance.metadata = validated_data.get("metadata", instance.metadata)
        instance.save()
        return instance


class CheckoutItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckoutItem
        fields = ["id", "product", "name", "sku", "price", "currency", "quantity", "metadata"]
        read_only_fields = fields


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "provider", "external_id", "status", "payload", "created_at"]
        read_only_fields = fields


class CheckoutSerializer(serializers.ModelSerializer):
    items = CheckoutItemSerializer(many=True, read_only=True)
    transactions = TransactionSerializer(many=True, read_only=True)
    basket_item_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=True, allow_empty=False
    )
    payment_confirmation = serializers.SerializerMethodField()

    class Meta:
        model = Checkout
        fields = [
            "id",
            "status",
            "payment_method",
            "delivery_method",
            "total_amount",
            "currency",
            "delivery_price",
            "payment_fee",
            "recipient_data",
            "items_snapshot",
            "notes",
            "items",
            "transactions",
            "basket_item_ids",
            "payment_confirmation",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "status",
            "total_amount",
            "currency",
            "delivery_price",
            "payment_fee",
            "items_snapshot",
            "created_at",
            "updated_at",
        )

    def get_payment_confirmation(self, obj):
        last_transaction = obj.transactions.first()
        if last_transaction and "confirmation_url" in last_transaction.payload:
            return {
                "confirmation_url": last_transaction.payload["confirmation_url"],
                "provider": last_transaction.provider,
                "status": last_transaction.status,
            }
        return None

    def validate_basket_item_ids(self, value):
        if not value:
            raise serializers.ValidationError("Необходимо выбрать хотя бы один товар.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        basket_item_ids: List[int] = validated_data.pop("basket_item_ids")
        basket_items = list(BasketItem.objects.select_related("product").filter(user_id=user.id, id__in=basket_item_ids))
        if not basket_items:
            raise serializers.ValidationError({"basket_item_ids": "Корзина пуста или не найдены элементы."})

        payment_method: PaymentMethod = validated_data["payment_method"]
        delivery_method: DeliveryMethod = validated_data["delivery_method"]

        currency = basket_items[0].currency
        subtotal = sum(item.price * item.count for item in basket_items)
        weight_kg = sum((item.product.weight_grams * item.count) / 1000 for item in basket_items)
        delivery_price = delivery_method.base_price + delivery_method.price_per_kg * Decimal(str(weight_kg))
        payment_fee = subtotal * (payment_method.fee_percent / Decimal("100"))

        snapshot = [
            {
                "product_id": item.product_id,
                "name": item.product.name,
                "sku": item.product.sku,
                "count": item.count,
                "unit_price": str(item.price),
                "variant": item.variant_data,
            }
            for item in basket_items
        ]

        checkout = Checkout.objects.create(
            user_id=user.id,
            total_amount=subtotal + delivery_price + payment_fee,
            currency=currency,
            delivery_price=delivery_price,
            payment_fee=payment_fee,
            items_snapshot=snapshot,
            **validated_data,
        )

        for item in basket_items:
            CheckoutItem.objects.create(
                checkout=checkout,
                product=item.product,
                name=item.product.name,
                sku=item.product.sku,
                price=item.price,
                currency=item.currency,
                quantity=item.count,
                metadata=item.variant_data,
            )
        BasketItem.objects.filter(id__in=[item.id for item in basket_items]).delete()

        return_url = self.context["request"].data.get("return_url") or getattr(
            settings, "CHECKOUT_RETURN_URL", "https://example.com/orders/success"
        )
        payment_payload = create_payment(checkout, return_url=return_url)
        Transaction.objects.create(
            checkout=checkout,
            provider=payment_payload.get("provider", "yookassa"),
            external_id=payment_payload["id"],
            status=payment_payload.get("status", "initiated"),
            payload=payment_payload,
        )
        publish_checkout_event(checkout)
        return checkout


class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("name", "code")
    ordering_fields = ("name",)


class DeliveryMethodViewSet(viewsets.ModelViewSet):
    queryset = DeliveryMethod.objects.all()
    serializer_class = DeliveryMethodSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("name", "code")
    ordering_fields = ("name",)


class BasketItemViewSet(viewsets.ModelViewSet):
    serializer_class = BasketItemSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return (
            BasketItem.objects.select_related("product")
            .filter(user_id=self.request.user.id)
            .order_by("-created_at")
        )


class CheckoutViewSet(viewsets.ModelViewSet):
    serializer_class = CheckoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        qs = Checkout.objects.select_related("payment_method", "delivery_method").prefetch_related("items", "transactions")
        if self.request.user.is_staff and self.request.query_params.get("all") == "true":
            return qs
        return qs.filter(user_id=self.request.user.id)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.select_related("checkout").all()
    serializer_class = TransactionSerializer
    permission_classes = (permissions.IsAdminUser,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("external_id", "provider")
    ordering_fields = ("created_at",)


