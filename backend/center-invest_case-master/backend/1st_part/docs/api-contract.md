# API Contract (working)

## Auth
- `POST /auth/register`
  - req: `{ "email": "user@example.com", "password": "string" }`
  - res: `{ "id": 1, "email": "user@example.com", "is_active": true }`
- `POST /auth/login`
  - req: `{ "email": "user@example.com", "password": "string" }`
  - res: `{ "access_token": "jwt", "token_type": "bearer" }`

## Users
- `GET /users/me`
  - header: `Authorization: Bearer <token>`
  - res: `{ "id": 1, "email": "user@example.com", "is_active": true }`

## Scenarios
- `GET /scenarios`
  - res: `[{ "id": 1, "title": "Office", "description": "..." }]`
- `GET /scenarios/{id}`
  - res: `{ "id": 1, "title": "Office", "description": "..." }`
- `GET /scenarios/{id}/missions`
  - res: `[{ "id": 10, "scenario_id": 1, "title": "Email", "order_index": 1 }]`
- `GET /scenarios/missions/{id}/choices`
  - res: `[{ "id": 100, "attack_id": 55, "label": "Ignore", "hint": "..." }]`

## Progress
- `GET /progress`
  - header: `Authorization: Bearer <token>`
  - res: `[{ "scenario_id": 1, "success_rate": 80, "mistakes": 2 }]`
- `POST /progress`
  - header: `Authorization: Bearer <token>`
  - req: `{ "scenario_id": 1, "success_rate": 80, "mistakes": 2 }`
  - res: `{ "scenario_id": 1, "success_rate": 80, "mistakes": 2 }`

## Ratings
- `GET /ratings?limit=50`
  - res: `[{ "user_id": 1, "reputation": 120, "league": 2 }]`
