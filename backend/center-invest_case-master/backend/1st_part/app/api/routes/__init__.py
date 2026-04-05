from fastapi import APIRouter

from app.api.routes import auth, health, progress, ratings, scenarios, users

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(scenarios.router)
api_router.include_router(progress.router)
api_router.include_router(ratings.router)
