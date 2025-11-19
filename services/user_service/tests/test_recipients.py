import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from recipients.models import Recipient


@pytest.mark.django_db
def test_admin_can_list_recipients():
    User = get_user_model()
    admin = User.objects.create_superuser(email="admin@example.com", username="admin", password="pass1234")
    customer = User.objects.create_user(email="user@example.com", username="user", password="pass1234")
    Recipient.objects.create(user=customer, full_name="Иван Иванов", city="Москва", address_line1="Тверская 1")

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.get("/api/v1/recipients/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["full_name"] == "Иван Иванов"


@pytest.mark.django_db
def test_user_can_manage_own_recipients():
    User = get_user_model()
    user = User.objects.create_user(email="user@example.com", username="user", password="pass1234")

    client = APIClient()
    client.force_authenticate(user=user)

    payload = {"full_name": "Иван Иванов", "city": "Москва", "address_line1": "Тверская 1"}
    create_resp = client.post("/api/v1/me/recipients/", payload, format="json")
    assert create_resp.status_code == 201

    recipient_id = create_resp.data["id"]
    list_resp = client.get("/api/v1/me/recipients/")
    assert list_resp.status_code == 200
    assert len(list_resp.data) == 1

    delete_resp = client.delete(f"/api/v1/me/recipients/{recipient_id}/")
    assert delete_resp.status_code == 204
    assert Recipient.objects.count() == 0


