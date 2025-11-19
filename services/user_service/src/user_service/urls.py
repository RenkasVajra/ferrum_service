"""URL configuration for user service."""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from api.users import UserViewSet
from api.recipients import MyRecipientViewSet, RecipientViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"recipients", RecipientViewSet, basename="recipient")
router.register(r"me/recipients", MyRecipientViewSet, basename="my-recipient")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("api/v1/", include(router.urls)),
]

