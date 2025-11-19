import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from catalog.models import Category
from goods.models import Brand, Product
from orders.models import BasketItem, DeliveryMethod, PaymentMethod


@pytest.mark.django_db
def test_user_checkout_flow_creates_transaction(monkeypatch):
    client = APIClient()
    User = get_user_model()
    user = User.objects.create_user(username="user", email="user@example.com", password="pass1234")
    client.force_authenticate(user=user)

    category = Category.objects.create(name="Одежда", slug="clothes")
    brand = Brand.objects.create(name="Ferrum", slug="ferrum")
    product = Product.objects.create(
        name="Футболка",
        slug="tee",
        description="",
        category=category,
        brand=brand,
        sku="SKU1",
        price="990.00",
        currency="RUB",
        stock=50,
        is_published=True,
    )
    payment = PaymentMethod.objects.create(name="YooKassa", code="yookassa")
    delivery = DeliveryMethod.objects.create(name="CDEK", code="cdek", base_price="250.00")

    basket_resp = client.post(
        "/api/v1/me/basket-items/",
        {"product": product.id, "count": 2},
        format="json",
    )
    assert basket_resp.status_code == 201
    basket_id = basket_resp.data["id"]

    checkout_resp = client.post(
        "/api/v1/checkouts/",
        {
            "payment_method": payment.id,
            "delivery_method": delivery.id,
            "basket_item_ids": [basket_id],
            "recipient_data": {"full_name": "Иван Иванов"},
        },
        format="json",
    )
    assert checkout_resp.status_code == 201
    data = checkout_resp.data
    assert data["payment_confirmation"]["provider"] == "yookassa"
    assert data["items"][0]["sku"] == "SKU1"


