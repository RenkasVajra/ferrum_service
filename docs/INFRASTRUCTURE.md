# Infrastructure Plan

## Target Stack
- **Orchestrator**: k3s (single node dev) → k8s/AKS/EKS for prod. Optionally Docker Swarm for PoC via the same manifests.
- **Databases**: Managed PostgreSQL cluster (one logical DB per microservice) exposed via Secret-managed connection strings.
- **Cache & Events**: Redis 7 cluster (HA with sentinel) powering Django cache, Celery broker, and Streams for cross-service events.
- **Object Storage**: MinIO (S3-compatible) for product images, payment logos, page assets; accessible via dedicated bucket per service.
- **Message Broker (optional)**: NATS JetStream or Kafka for future high-volume analytics; Redis Streams covers MVP.
- **CI/CD**: GitHub Actions → build container images, push to registry, run pytest, upload coverage, deploy via `kubectl apply`.

## Deployment Layout
```
infrastructure/
 ├─ k8s/
 │   ├─ namespaces.yaml
 │   ├─ secrets/ (SOPS-encrypted)
 │   ├─ postgres/
 │   ├─ redis/
 │   ├─ minio/
 │   └─ services/
 │       ├─ auth-service.yaml
 │       ├─ user-service.yaml
 │       ├─ content-service.yaml
 │       └─ catalog-service.yaml
 └─ helm-values/ (if chartifying later)
```

Each deployment uses:
- RollingStrategy with minReadySeconds=10
- HorizontalPodAutoscaler (CPU 70%, min=1, max=5)
- ConfigMap for Django settings (`DJANGO_ALLOWED_HOSTS`, `REDIS_URL`, `DATABASE_URL`)
- Secret for `DJANGO_SECRET_KEY`, `YOOKASSA_*`, SMTP creds
- InitContainer running `python manage.py migrate`
- Sidecar `celery worker` + `celery beat` for async jobs where needed (`auth_service`, `catalog_service`)

## Networking
- Istio or Traefik ingress, exposing:
  - `api.ferrum.local/auth`
  - `api.ferrum.local/user`
  - `api.ferrum.local/content`
  - `api.ferrum.local/catalog`
- Redis + Postgres hidden via ClusterIP, accessible only inside namespace.

## Observability
- Prometheus Operator scraping Django `/metrics` (use `django-prometheus` later)
- Loki stack for logs (Fluent Bit daemonset collects container logs)
- Tempo (optional) if distributed tracing needed.

## Local Dev
- `docker compose` equivalent (to be generated):
  - `postgres` + `redis` + `minio` containers
  - separate Django containers per service
  - `traefik` as reverse proxy
- `make up` / `make down` wrappers for parity with k3s manifests.


