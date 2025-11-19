"""WSGI config for content_service project."""

from __future__ import annotations

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "content_service.settings")

application = get_wsgi_application()


