from __future__ import annotations

from django.urls import reverse
from rest_framework.test import APIClient

from authentication.models import OTPRequest


def test_login_creates_otp(db, monkeypatch):
    client = APIClient()
    monkeypatch.setattr("authentication.models.secrets.choice", lambda _: "1")

    response = client.post(reverse("authentication:login"), {"email": "user@example.com"}, format="json")

    assert response.status_code == 200
    assert OTPRequest.objects.filter(email="user@example.com").exists()
    otp = OTPRequest.objects.get(email="user@example.com")
    assert otp.code == "111111"


def test_confirm_returns_tokens(db):
    client = APIClient()
    OTPRequest.issue_code("user@example.com")
    otp = OTPRequest.objects.get(email="user@example.com")

    response = client.post(
        reverse("authentication:confirm"),
        {"email": "user@example.com", "code": otp.code},
        format="json",
    )

    assert response.status_code == 200
    data = response.json()
    assert "access" in data
    assert response.cookies.get("refresh_token") is not None

