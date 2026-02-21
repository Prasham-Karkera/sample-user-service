# ka-chow-user-service

> **Service:** User Management & Authentication  
> **Port:** 8001  
> **Team:** Identity  
> **Database:** `fb_users` (PostgreSQL)

## Service Overview

Manages FleetBite user accounts. Handles registration, profile management, login, and JWT issuance. All other services trust user identity via the JWT injected by the API Gateway (`X-FleetBite-User-ID` header).

## Architecture Role

```
API Gateway ──► [User Service :8001] ──► PostgreSQL (fb_users)
                      ↑
               JWT issuing authority
               (all other services verify, not issue)
```

## Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| PostgreSQL | Database | Persistent user store |
| API Gateway | Upstream | Routes external traffic here |

This service has **no downstream service calls** — it is a leaf in the dependency graph.

## API Reference

Full spec: [`docs/openapi.yaml`](docs/openapi.yaml)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/users/register` | Register new user |
| `GET` | `/v1/users/{user_id}` | Get user profile |
| `PATCH` | `/v1/users/{user_id}` | Update profile |
| `DELETE` | `/v1/users/{user_id}` | Deactivate user |
| `POST` | `/v1/auth/token` | Login, get JWT |
| `GET` | `/health/live` | Liveness |
| `GET` | `/health/ready` | Readiness |

## Data Model

**`usr_users`**
| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | Auto-generated |
| `email` | VARCHAR(255) | Unique |
| `hashed_password` | VARCHAR(255) | BCrypt |
| `full_name` | VARCHAR(255) | |
| `phone` | VARCHAR(20) | Nullable |
| `is_active` | BOOLEAN | Soft delete flag |
| `is_verified` | BOOLEAN | Email verification |
| `role` | VARCHAR(50) | `customer` \| `driver` \| `admin` |
| `created_at` | TIMESTAMPTZ | |
| `updated_at` | TIMESTAMPTZ | |

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `USR_DATABASE_URL` | ✅ | `postgresql+asyncpg://...` |
| `USR_JWT_SECRET_KEY` | ✅ | Must match Gateway secret |
| `USR_JWT_ALGORITHM` | — | Default: `HS256` |
| `USR_JWT_EXPIRY_SECONDS` | — | Default: `3600` |
| `USR_ENV` | — | Default: `development` |

## Running Locally

```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials
docker-compose up -d
curl http://localhost:8001/health/live
```

## Running Tests

```bash
pip install -e ".[dev]"
pytest --cov=app tests/
```
