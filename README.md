# Center-Invest Fullstack

Объединённый проект:

- `backend/` — основной FastAPI backend с авторизацией, кабинетами, прогрессом, рейтингом и сценариями
- `frontend/` — Next.js интерфейс, интегрированный с актуальными `api/v1` endpoint-ами backend

## Быстрый старт

### Вариант 1. Docker Compose

```bash
docker compose up --build
```

После запуска:

- frontend: `http://localhost:3000`
- backend API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

### Вариант 2. Локально

Backend:

```bash
cd backend
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Что реализовано по ТЗ

- регистрация, логин, JWT, сессии
- профиль пользователя и личный кабинет
- трекинг прогресса, ошибок, процентов успешности
- рейтинг, лиги, репутация
- интерактивные сценарии с пошаговым прохождением
- frontend на Next.js, совместимый с текущим backend

## Важно

По твоему отдельному запросу backend сейчас использует `SQLite` вместо `PostgreSQL`, чтобы проект запускался проще. Если понадобится вернуть строгий PostgreSQL-стек, это можно сделать отдельным проходом без переделки frontend.
