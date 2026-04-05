# CentreInvest Simulator (backend)

## Quick Start (Local)
```bash
cd /Users/danil/кодинг/хак/centre_invest
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m alembic upgrade head
uvicorn app.main:app --reload
```

API: `http://localhost:8000`
Swagger: `http://localhost:8000/docs`

## Docker
Dev:
```bash
docker compose -f docker-compose.dev.yml up --build
```

Prod:
```bash
docker compose -f docker-compose.prod.yml up --build
```

## Migrations
```bash
python -m alembic upgrade head
```

## Auth Flow (minimal)
1. Register: `POST /auth/register`
2. Login: `POST /auth/login`
3. Use token: `Authorization: Bearer <token>`

## Environment
Key vars in `.env`:
- `DATABASE_URL` (SQLite by default)
- `SECRET_KEY` (JWT signing)
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `ALLOWED_ORIGINS`
- `ENABLE_RATE_LIMIT`
- `RATE_LIMIT_PER_MINUTE`

## TLS
TLS is expected to be terminated by a reverse proxy (Caddy/Nginx) in production.

## Structure
- `app/api/routes` – HTTP endpoints
- `app/api/deps.py` – auth dependencies
- `app/core` – config, security, rate limiting
- `app/models` – SQLAlchemy models
- `app/schemas` – Pydantic schemas
- `app/services` – business logic
- `app/repos` – DB access
- `app/db/migrations` – Alembic migrations
- `docs/er.md` – ER diagram
- `docs/api-contract.md` – API contract draft
