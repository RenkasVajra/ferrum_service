"""URL configuration for catalog service."""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from api.catalog import CategoryViewSet
from api.goods import BrandViewSet, ProductViewSet, SizeViewSet
from api.orders import (
    BasketItemViewSet,
    CheckoutViewSet,
    DeliveryMethodViewSet,
    PaymentMethodViewSet,
    TransactionViewSet,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"brands", BrandViewSet, basename="brand")
router.register(r"sizes", SizeViewSet, basename="size")
router.register(r"goods", ProductViewSet, basename="product")
router.register(r"payments/methods", PaymentMethodViewSet, basename="payment-method")
router.register(r"deliveries/methods", DeliveryMethodViewSet, basename="delivery-method")
router.register(r"me/basket-items", BasketItemViewSet, basename="basket-item")
router.register(r"checkouts", CheckoutViewSet, basename="checkout")
router.register(r"transactions", TransactionViewSet, basename="transaction")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("api/v1/", include(router.urls)),
]


