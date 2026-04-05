from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AccessContext, get_access_context
from app.core.database import get_db_session
from app.core.redis import get_redis
from app.schemas.rating import LeaderboardResponse, RatingOverviewResponse
from app.services.rating import rating_service

router = APIRouter()


@router.get("/me", response_model=RatingOverviewResponse)
async def my_rating(
    context: AccessContext = Depends(get_access_context),
    db: AsyncSession = Depends(get_db_session),
) -> RatingOverviewResponse:
    data = await rating_service.get_rating_overview(db, context.user)
    return RatingOverviewResponse(**data)


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def leaderboard(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> LeaderboardResponse:
    data = await rating_service.get_leaderboard(db, redis, limit=limit, offset=offset)
    return LeaderboardResponse(**data)
