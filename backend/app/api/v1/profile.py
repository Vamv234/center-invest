from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AccessContext, get_access_context
from app.core.database import get_db_session
from app.schemas.profile import CabinetResponse, ProfileRead, ProfileUpdate
from app.services.profile import profile_service

router = APIRouter()


@router.get("/me", response_model=ProfileRead)
async def get_my_profile(context: AccessContext = Depends(get_access_context)) -> ProfileRead:
    return ProfileRead.model_validate(context.user)


@router.patch("/me", response_model=ProfileRead)
async def update_my_profile(
    payload: ProfileUpdate,
    context: AccessContext = Depends(get_access_context),
    db: AsyncSession = Depends(get_db_session),
) -> ProfileRead:
    user = await profile_service.update_profile(db, context.user, payload)
    return ProfileRead.model_validate(user)


@router.get("/me/cabinet", response_model=CabinetResponse)
async def get_my_cabinet(
    context: AccessContext = Depends(get_access_context),
    db: AsyncSession = Depends(get_db_session),
) -> CabinetResponse:
    cabinet = await profile_service.get_cabinet(db, context.user)
    return CabinetResponse(
        profile=ProfileRead.model_validate(cabinet["profile"]),
        stats=cabinet["stats"],
        active_sessions=cabinet["active_sessions"],
        current_rank=cabinet["current_rank"],
        recent_progress=cabinet["recent_progress"],
        recent_reputation_events=cabinet["recent_reputation_events"],
    )
