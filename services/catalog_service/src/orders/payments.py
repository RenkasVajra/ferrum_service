from __future__ import annotations

import base64
import logging
import uuid

import requests
from django.conf import settings

from .models import Checkout

logger = logging.getLogger(__name__)


def _auth_header() -> str:
    token = f"{settings.YOOKASSA_SHOP_ID}:{settings.YOOKASSA_API_KEY}"
    return base64.b64encode(token.encode()).decode()


def create_payment(checkout: Checkout, return_url: str) -> dict:
    """
    Create YooKassa payment. Falls back to mock payload if credentials are missing.
    """
    if not settings.YOOKASSA_SHOP_ID or not settings.YOOKASSA_API_KEY:
        logger.warning("YOOKASSA credentials not configured, returning mock payment payload.")
        return {
            "id": f"mock-{checkout.id}",
            "status": "pending",
            "provider": "yookassa",
            "confirmation_url": return_url,
            "amount": {"value": str(checkout.total_amount), "currency": checkout.currency},
        }

    payload = {
        "amount": {"value": str(checkout.total_amount), "currency": checkout.currency},
        "confirmation": {"type": "redirect", "return_url": return_url},
        "capture": True,
        "description": f"Checkout #{checkout.id}",
        "metadata": {"checkout_id": checkout.id},
    }
    headers = {
        "Idempotence-Key": str(uuid.uuid4()),
        "Authorization": f"Basic {_auth_header()}",
        "Content-Type": "application/json",
    }
    response = requests.post("https://api.yookassa.ru/v3/payments", json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()
    data["provider"] = "yookassa"
    return data


