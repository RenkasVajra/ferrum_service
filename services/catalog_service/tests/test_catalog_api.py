import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from catalog.models import Category
from goods.models import Brand, Product, Size


@pytest.mark.django_db
def test_admin_can_create_category_tree_and_list_tree():
    client = APIClient()
    User = get_user_model()
    admin = User.objects.create_superuser(username="admin", email="admin@example.com", password="pass1234")
    client.force_authenticate(user=admin)

    root_resp = client.post(
        "/api/v1/categories/",
        {"name": "Одежда", "slug": "clothes"},
        format="json",
    )
    assert root_resp.status_code == 201
    root_id = root_resp.data["id"]

    child_resp = client.post(
        "/api/v1/categories/",
        {"name": "Футболки", "slug": "tshirts", "parent": root_id},
        format="json",
    )
    assert child_resp.status_code == 201

    list_resp = client.get("/api/v1/categories/?tree=true")
    assert list_resp.status_code == 200
    assert list_resp.data[0]["children"][0]["slug"] == "tshirts"


@pytest.mark.django_db
def test_product_creation_and_public_listing():
    client = APIClient()
    User = get_user_model()
    admin = User.objects.create_superuser(username="admin", email="admin@example.com", password="pass1234")
    client.force_authenticate(user=admin)

    category = Category.objects.create(name="Одежда", slug="clothes")
    brand = Brand.objects.create(name="Ferrum", slug="ferrum")
    size = Size.objects.create(name="M", code="M")

    payload = {
        "name": "Футболка Ferrum",
        "slug": "tee-ferrum",
        "description": "Базовая футболка",
        "category": category.id,
        "brand_id": brand.id,
        "sku": "SKU123",
        "price": "1990.00",
        "currency": "RUB",
        "status": "in_stock",
        "is_published": True,
        "sizes_info": [
            {
                "size_id": size.id,
                "price_modifier": "0.00",
                "stock": 10,
            }
        ],
    }

    create_resp = client.post("/api/v1/goods/", payload, format="json")
    assert create_resp.status_code == 201

    client.force_authenticate(user=None)
    list_resp = client.get("/api/v1/goods/?is_published=true")
    assert list_resp.status_code == 200
    assert list_resp.data[0]["slug"] == "tee-ferrum"


