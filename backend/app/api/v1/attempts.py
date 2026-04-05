from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AccessContext, get_access_context
from app.core.database import get_db_session
from app.core.redis import get_redis
from app.schemas.scenario_gameplay import (
    AttemptAnswerResultOut,
    AttemptEventOut,
    AttemptStateOut,
    HintResultOut,
    SubmitAnswerIn,
)
from app.services.scenario_gameplay import scenario_gameplay_service

router = APIRouter()


@router.get("/{attempt_id}", response_model=AttemptStateOut)
async def get_attempt(
    attempt_id: UUID,
    context: AccessContext = Depends(get_access_context),
    db: AsyncSession = Depends(get_db_session),
) -> AttemptStateOut:
    return await scenario_gameplay_service.get_attempt_state(
        db,
        user=context.user,
        attempt_id=attempt_id,
    )


@router.post("/{attempt_id}/answers", response_model=AttemptAnswerResultOut)
async def submit_answer(
    attempt_id: UUID,
    payload: SubmitAnswerIn,
    context: AccessContext = Depends(get_access_context),
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> AttemptAnswerResultOut:
    return await scenario_gameplay_service.submit_answer(
        db,
        redis,
        user=context.user,
        attempt_id=attempt_id,
        option_id=payload.option_id,
    )


@router.post("/{attempt_id}/hint", response_model=HintResultOut)
async def use_hint(
    attempt_id: UUID,
    context: AccessContext = Depends(get_access_context),
    db: AsyncSession = Depends(get_db_session),
) -> HintResultOut:
    return await scenario_gameplay_service.use_hint(
        db,
        user=context.user,
        attempt_id=attempt_id,
    )


@router.get("/{attempt_id}/events", response_model=list[AttemptEventOut])
async def list_attempt_events(
    attempt_id: UUID,
    context: AccessContext = Depends(get_access_context),
    db: AsyncSession = Depends(get_db_session),
) -> list[AttemptEventOut]:
    return await scenario_gameplay_service.list_attempt_events(
        db,
        user=context.user,
        attempt_id=attempt_id,
    )
