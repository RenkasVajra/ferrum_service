# Changelog

## [0.2.0] - 2025-11-26
- Подготовлен Dockerfile и интеграция в общий docker-compose стек (Postgres, Redis, MinIO).
- Включены CORS/CSRF настройки для клиентского Next.js и админской PWA.
- Добавлены gunicorn и переменные окружения для публикации событий/платежных настроек.

## [0.1.0] - 2025-11-19
- Scaffolded catalog service with categories, brands, sizes, and product CRUD plus Redis product events.
- Implemented payment and delivery methods, basket, checkout flow, YooKassa integration, and Redis checkout events.
- Added pytest suites covering catalog trees, product publishing, and checkout happy path.


