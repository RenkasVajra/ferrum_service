FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

COPY services/content_service/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

COPY services/content_service /app
COPY docker/django-entrypoint.sh /entrypoint.sh
COPY docker/wait-for-it.sh /wait-for-it.sh

RUN chmod +x /entrypoint.sh /wait-for-it.sh

ENV PYTHONPATH=/app/src

EXPOSE 8000

ENTRYPOINT ["sh", "entrypoint.sh"]
CMD ["gunicorn", "content_service.wsgi:application", "--bind", "0.0.0.0:8000"]


