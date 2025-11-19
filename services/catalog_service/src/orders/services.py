from __future__ import annotations

import logging

from django.conf import settings
from django_redis import get_redis_connection

from .models import Checkout

logger = logging.getLogger(__name__)


def publish_checkout_event(checkout: Checkout) -> None:
    stream = getattr(settings, "CHECKOUT_STREAM", None)
    if not stream:
        return
    payload = {
        "checkout_id": str(checkout.id),
        "user_id": str(checkout.user_id),
        "status": checkout.status,
        "total": str(checkout.total_amount),
    }
    try:
        conn = get_redis_connection("default")
        conn.xadd(stream, payload)
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to push checkout event: %s", exc)


