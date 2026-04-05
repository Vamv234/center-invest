from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import attempts, auth, health, profile, progress, rating, scenarios, ws

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])
api_router.include_router(rating.router, prefix="/rating", tags=["rating"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
api_router.include_router(attempts.router, prefix="/attempts", tags=["attempts"])
api_router.include_router(ws.router, prefix="/ws", tags=["websocket"])
