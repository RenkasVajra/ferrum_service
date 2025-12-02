#!/bin/sh
set -euo pipefail

if [ -n "${WAIT_FOR_TARGET:-}" ]; then
  /wait-for-it.sh "${WAIT_FOR_TARGET}" true
fi

python manage.py migrate --noinput

if [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  python manage.py shell <<'PYCODE'
from django.contrib.auth import get_user_model
import os

User = get_user_model()
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")

if email and password and not User.objects.filter(email=email).exists():
    User.objects.create_superuser(username=username or email, email=email, password=password)
PYCODE
fi

python manage.py collectstatic --noinput

exec "$@"


