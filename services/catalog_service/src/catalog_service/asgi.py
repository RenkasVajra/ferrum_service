"""
ASGI config for catalog_service project.
"""

from __future__ import annotations

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "catalog_service.settings")

application = get_asgi_application()


