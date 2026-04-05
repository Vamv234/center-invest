from __future__ import annotations

import json

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AccessContext, get_access_context
from app.core.database import get_db_session
from app.core.redis import get_redis
from app.schemas.scenario_gameplay import AttemptStateOut, ScenarioCard
from app.services.scenario_gameplay import scenario_gameplay_service

router = APIRouter()

SCENARIOS_CACHE_TTL = 3600  # 1 hour


@router.get("", response_model=list[ScenarioCard])
async def list_scenarios(
    db: AsyncSession = Depends(get_db_session),
    redis = Depends(get_redis),
) -> list[ScenarioCard]:
    """List all available scenarios with caching support."""
    # Try to get from cache first
    cache_key = "scenarios:list"
    try:
        cached = await redis.get(cache_key)
        if cached:
            data = json.loads(cached)
            return [ScenarioCard(**item) for item in data]
    except Exception:
        # Cache miss or error - fall through to database
        pass
    
    # Get from database
    scenarios = await scenario_gameplay_service.list_scenarios(db)
    
    # Cache the results
    try:
        cache_data = json.dumps([s.model_dump() for s in scenarios])
        await redis.setex(cache_key, SCENARIOS_CACHE_TTL, cache_data)
    except Exception:
        # Cache write failure - continue anyway
        pass
    
    return scenarios


@router.post("/{scenario_id}/attempts", response_model=AttemptStateOut, status_code=status.HTTP_201_CREATED)
async def start_attempt(
    scenario_id: str,
    context: AccessContext = Depends(get_access_context),
    db: AsyncSession = Depends(get_db_session),
) -> AttemptStateOut:
    """Start a new training attempt for a scenario."""
    return await scenario_gameplay_service.start_attempt(
        db,
        user=context.user,
        scenario_id=scenario_id,
    )
