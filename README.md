# Ferrum Commerce Constructor

Микросервисная учебная система для сборки интернет‑магазинов. Репозиторий содержит backend‑сервисы на Django, клиентский Next.js фронтенд, админскую PWA на React/Vite, а также инфраструктурные артефакты для развёртывания в Docker Compose/k3s.

## Состав решений

- **services/auth_service** — OTP авторизация и выдача JWT.
- **services/user_service** — управление пользователями и получателями.
- **services/content_service** — новости, страницы и changelog контента.
- **services/catalog_service** — каталог, товары, корзины, оплаты и доставки.
- **apps/client-web** — публичный Next.js фронтенд (TypeScript, SEO friendly).
- **apps/admin-pwa** — админка на React + Vite + Redux Toolkit + PWA.
- **docs/** — инфраструктура, тестирование и методички.
- **docker-compose.yml** — оркестрация Postgres, Redis, MinIO и всех сервисов.

Каждый сервис имеет собственный `CHANGELOG.md` и OpenAPI (drf-spectacular). Все контейнеры могут быть перенесены в k3s/k8s/Swarm без изменения образов.

## Быстрый старт (Docker Compose)

1. Скопируйте переменные окружения и отредактируйте при необходимости:
   ```bash
   cp env.example .env
   ```
2. Соберите и поднимите весь стек:
   ```bash
   docker compose up --build
   ```
3. После старта станут доступны:
   - Auth API — http://localhost:8101/api/docs/
   - User API — http://localhost:8102/api/docs/
   - Content API — http://localhost:8103/api/docs/
   - Catalog API — http://localhost:8104/api/docs/
   - Клиентский фронт — http://localhost:3000
   - Админская PWA — http://localhost:4173
4. Для остановки:
   ```bash
   docker compose down
   ```

> Compose-сервисы автоматически выполняют миграции и создают суперпользователя `admin@example.com`/`admin1234` (см. `.env.example`). Код отправки OTP в dev-режиме попадает в логи контейнера auth_service.

## Ручной запуск (без Docker)

1. Установите зависимости для каждого Django-сервиса (`pip install -r requirements.txt`) и запустите `python manage.py migrate && python manage.py runserver 0.0.0.0:8XXX`.
2. Установите Node.js 20+. Для публичного фронта:
   ```bash
   cd apps/client-web
   npm install
   npm run dev
   ```
3. Для админки:
   ```bash
   cd apps/admin-pwa
   npm install
   npm run dev
   ```
4. Экспортируйте переменные `NEXT_PUBLIC_*`/`VITE_*`, чтобы фронты знали базовые URL сервисов (пример — в `.env.example`).

## Admin PWA: функциональность и окружение

- PWA-шелл на React + Vite, оффлайн-кеширование (`public/sw.js`) и манифест.
- Авторизация через OTP (`auth_service`) с сохранением `accessToken` в Redux Toolkit.
- Первый реализованный модуль — CRUD дерева категорий (`catalog_service/api/v1/categories`), в том числе построение древовидного списка и форма редактирования.
- Конфигурация окружения:
  - `VITE_AUTH_API_URL` — базовый URL Auth API (например, `http://localhost:8101/api/v1`).
  - `VITE_CATALOG_API_URL` — URL Catalog API (`http://localhost:8104/api/v1`).
- Основные команды:
  ```bash
  cd apps/admin-pwa
  npm install
  npm run dev      # http://localhost:4173
  npm run build    # production bundle (dist/)
  npm run preview  # локальный предпросмотр
  ```

## Тесты

```bash
cd services/catalog_service && pytest --cov=.
cd services/content_service && pytest --cov=.
cd services/user_service && pytest --cov=.
cd services/auth_service && pytest --cov=.
```

В CI целевой порог покрытия — 80% (см. `pytest.ini`). Frontend-проекты содержат `npm run typecheck`/`npm run lint`.

## Архитектура взаимодействия

- JWT, выданный `auth_service`, используется всеми фронтами и админским API.
- Redis выступает кэшем Django и транспортом событий (Streams) для публикаций товаров/новостей/чекаутов.
- MinIO хранит медиа (логотипы оплат, изображения товаров). В dev-режиме используются локальные файловые бэкенды.
- Frontend приложения взаимодействуют с API напрямую (на локали каждая служба доступна по своему порту). В production предполагается Traefik/Ingress с маршрутами `/auth`, `/user`, `/content`, `/catalog`.



