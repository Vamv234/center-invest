from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AccessContext, get_access_context
from app.core.database import get_db_session
from app.core.redis import get_redis
from app.schemas.progress import (
    ProgressSubmissionResponse,
    ProgressSummaryResponse,
    ScenarioAttemptCreate,
    ScenarioProgressDetail,
    ScenarioProgressRead,
)
from app.services.progress import progress_service

router = APIRouter()


@router.post("/attempts", response_model=ProgressSubmissionResponse, status_code=status.HTTP_201_CREATED)
async def submit_attempt(
    payload: ScenarioAttemptCreate,
    context: AccessContext = Depends(get_access_context),
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> ProgressSubmissionResponse:
    result = await progress_service.submit_attempt(db, redis, user=context.user, payload=payload)
    return ProgressSubmissionResponse(**result)


@router.get("/summary", response_model=ProgressSummaryResponse)
async def get_progress_summary(
    context: AccessContext = Depends(get_access_context),
    db: AsyncSession = Depends(get_db_session),
) -> ProgressSummaryResponse:
    summary = await progress_service.get_progress_summary(db, context.user)
    return ProgressSummaryResponse(**summary)


@router.get("/scenarios", response_model=list[ScenarioProgressRead])
async def list_scenarios(
    context: AccessContext = Depends(get_access_context),
    db: AsyncSession = Depends(get_db_session),
) -> list[ScenarioProgressRead]:
    progress = await progress_service.list_progress(db, context.user)
    return [ScenarioProgressRead.model_validate(item) for item in progress]


@router.get("/scenarios/{scenario_key}", response_model=ScenarioProgressDetail)
async def get_scenario_progress(
    scenario_key: str,
    context: AccessContext = Depends(get_access_context),
    db: AsyncSession = Depends(get_db_session),
) -> ScenarioProgressDetail:
    detail = await progress_service.get_progress_detail(db, context.user, scenario_key)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found.")
    return ScenarioProgressDetail(**detail)
