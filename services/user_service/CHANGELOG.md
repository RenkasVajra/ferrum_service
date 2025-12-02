# Changelog

## [0.2.0] - 2025-11-26
- Добавлены Dockerfile/requirements для контейнеризации сервиса.
- Включены CORS/CSRF настройки для взаимодействия с Next.js и админской PWA.
- Обновлён docker-compose стек для автоматического старта миграций и суперпользователя.

## [0.1.0] - 2025-11-19
- Added recipients domain (models, admin serializers, migrations) with admin and self-service APIs.
- Wired pytest suite covering admin listing and end-user CRUD for shipping addresses.
- Configured pytest.ini, REST settings, and routers to expose new endpoints via Spectacular docs.


