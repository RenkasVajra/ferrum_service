import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from pages.models import Page, PageTemplate


@pytest.mark.django_db
def test_admin_can_create_template_and_page():
    client = APIClient()
    User = get_user_model()
    admin = User.objects.create_superuser(username="admin", email="admin@example.com", password="pass1234")
    client.force_authenticate(user=admin)

    template_payload = {
        "name": "Landing",
        "slug": "landing",
        "schema": {"sections": [{"type": "hero"}]},
    }
    template_response = client.post("/api/v1/pages/templates/", template_payload, format="json")
    assert template_response.status_code == 201
    template_id = template_response.json()["id"]

    page_payload = {
        "title": "Главная",
        "slug": "home",
        "status": "published",
        "template_id": template_id,
        "blocks": {"sections": [{"type": "hero", "props": {"title": "Ferrum"}}]},
    }
    page_response = client.post("/api/v1/pages/", page_payload, format="json")
    assert page_response.status_code == 201
    page = Page.objects.get(slug="home")
    assert page.template_id == template_id
    assert page.status == Page.Status.PUBLISHED
    assert page.events.count() == 1


@pytest.mark.django_db
def test_public_page_endpoint_returns_published_page():
    template = PageTemplate.objects.create(name="Landing", slug="landing")
    Page.objects.create(
        title="Главная",
        slug="home",
        status=Page.Status.PUBLISHED,
        template=template,
        blocks={"sections": []},
    )

    client = APIClient()
    response = client.get("/api/v1/pages/published/home/")

    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "home"


