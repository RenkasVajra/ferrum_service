from __future__ import annotations

import logging

from django.conf import settings
from django_redis import get_redis_connection
from rest_framework import filters, serializers, viewsets

from catalog.models import Category
from common.permissions import IsAdminOrReadOnly
from goods.models import Brand, Product, ProductImage, ProductSize, Size

logger = logging.getLogger(__name__)


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "slug", "description", "country", "website", "logo", "created_at", "updated_at"]
        read_only_fields = ("created_at", "updated_at")


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ["id", "name", "code", "size_type", "description", "measurements"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "position"]


class ProductSizeSerializer(serializers.ModelSerializer):
    size = SizeSerializer(read_only=True)
    size_id = serializers.PrimaryKeyRelatedField(
        queryset=Size.objects.all(), source="size", write_only=True, required=True
    )

    class Meta:
        model = ProductSize
        fields = ["id", "size", "size_id", "price_modifier", "stock"]


class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(), source="brand", write_only=True, required=True
    )
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    images = ProductImageSerializer(many=True, required=False)
    sizes_info = ProductSizeSerializer(source="productsize_set", many=True, required=False)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "category",
            "brand",
            "brand_id",
            "sku",
            "price",
            "currency",
            "status",
            "is_published",
            "attributes",
            "meta",
            "stock",
            "weight_grams",
            "images",
            "sizes_info",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("created_at", "updated_at")

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        sizes_data = validated_data.pop("productsize_set", [])
        product = super().create(validated_data)
        self._sync_images(product, images_data)
        self._sync_sizes(product, sizes_data)
        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images", None)
        sizes_data = validated_data.pop("productsize_set", None)
        product = super().update(instance, validated_data)
        if images_data is not None:
            instance.images.all().delete()
            self._sync_images(product, images_data)
        if sizes_data is not None:
            ProductSize.objects.filter(product=product).delete()
            self._sync_sizes(product, sizes_data)
        return product

    def _sync_images(self, product, images_data):
        for index, image_data in enumerate(images_data):
            ProductImage.objects.create(product=product, position=image_data.get("position", index), **image_data)

    def _sync_sizes(self, product, sizes_data):
        for size_data in sizes_data:
            size = size_data.get("size")
            ProductSize.objects.create(
                product=product,
                size=size,
                price_modifier=size_data.get("price_modifier", 0),
                stock=size_data.get("stock", 0),
            )


def publish_product_event(product: Product) -> None:
    stream = getattr(settings, "PRODUCT_STREAM", None)
    if not stream or not product.is_published:
        return
    payload = {
        "product_id": str(product.id),
        "slug": product.slug,
        "name": product.name,
        "sku": product.sku,
        "price": str(product.price),
        "currency": product.currency,
        "category_id": str(product.category_id),
    }
    try:
        conn = get_redis_connection("default")
        stream_id = conn.xadd(stream, payload)
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to push product event: %s", exc)
        stream_id = "offline"
    meta = product.meta or {}
    meta["last_stream_id"] = stream_id
    product.meta = meta
    product.save(update_fields=["meta"])


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("name", "slug")
    ordering_fields = ("name", "created_at")


class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("name", "code")
    ordering_fields = ("name",)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("brand", "category").prefetch_related("images", "sizes").all()
    serializer_class = ProductSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("name", "slug", "sku")
    ordering_fields = ("created_at", "price")
    filterset_fields = ("category", "brand", "status", "is_published")

    def perform_create(self, serializer):
        product = serializer.save()
        publish_product_event(product)

    def perform_update(self, serializer):
        product = serializer.save()
        publish_product_event(product)


