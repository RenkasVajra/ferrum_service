import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from news.models import NewsArticle, NewsEvent


@pytest.mark.django_db
def test_admin_can_create_and_publish_news():
    client = APIClient()
    User = get_user_model()
    admin = User.objects.create_superuser(username="admin", email="admin@example.com", password="pass1234")
    client.force_authenticate(user=admin)

    payload = {
        "title": "Запуск конструктора",
        "slug": "site-builder-release",
        "summary": "Коротко о релизе конструктора",
        "body": "Полное описание релиза",
        "status": "published",
        "tags": ["release", "builder"],
        "changelog": [
            {
                "title": "Добавлен drag-n-drop",
                "description": "Теперь можно собирать блоки мышкой",
                "impact_area": "Фронтенд",
                "change_type": "added",
                "metadata": {"version": "1.0"},
            }
        ],
    }

    response = client.post("/api/v1/news/", payload, format="json")

    assert response.status_code == 201
    article = NewsArticle.objects.get(slug="site-builder-release")
    assert article.status == NewsArticle.Status.PUBLISHED
    assert article.changelog.count() == 1
    # event persists even if redis is offline (stream_id='offline')
    assert NewsEvent.objects.filter(article=article).exists()


@pytest.mark.django_db
def test_public_news_list_only_returns_published():
    NewsArticle.objects.create(title="draft", slug="draft", body="...", status=NewsArticle.Status.DRAFT)
    NewsArticle.objects.create(
        title="published",
        slug="published",
        body="...",
        status=NewsArticle.Status.PUBLISHED,
    )

    client = APIClient()
    response = client.get("/api/v1/public/news/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["slug"] == "published"


