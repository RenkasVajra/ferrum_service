# Testing & QA Notes

## Local commands
```bash
# Auth service (already shipped)
cd services/auth_service && py -3 -m pytest

# Content service
cd services/content_service && py -3 -m pytest

# User service
cd services/user_service && py -3 -m pytest

# Catalog service
cd services/catalog_service && py -3 -m pytest
```

## Current status (2025‑11‑19)
- `content_service`: ✅ covers news publishing + page builder public/admin flows.
- `user_service`: ✅ covers admin list + end-user CRUD for recipients.
- `catalog_service`: ✅ covers category tree, product creation, and checkout happy path.
- `auth_service`: already had OTP flow tests earlier; rerun if changes are made.

## Next steps
- Add integration tests for YooKassa webhook + transaction status updates once gateway creds are connected.
- Extend catalog tests with stock reservation & multi-variant baskets.
- Wire frontend e2e tests (Playwright) when Next.js client is ready.


