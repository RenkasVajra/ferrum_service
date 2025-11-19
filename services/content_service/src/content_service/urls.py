"""URL configuration for the content service."""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from api.news import NewsViewSet, PublicNewsViewSet
from api.pages import PageTemplateViewSet, PageViewSet, PublishedPageViewSet

router = DefaultRouter()
router.register(r"news", NewsViewSet, basename="news")
router.register(r"pages", PageViewSet, basename="page")
router.register(r"pages/templates", PageTemplateViewSet, basename="page-template")
router.register(r"pages/published", PublishedPageViewSet, basename="published-page")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("api/v1/", include(router.urls)),
    path("api/v1/public/news/", PublicNewsViewSet.as_view({"get": "list"}), name="public-news-list"),
    path(
        "api/v1/public/news/<int:pk>/",
        PublicNewsViewSet.as_view({"get": "retrieve"}),
        name="public-news-detail",
    ),
]


