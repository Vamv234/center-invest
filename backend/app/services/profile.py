from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import ScenarioProgress
from app.models.reputation import ReputationLedger
from app.models.session import UserSession
from app.models.user import User
from app.schemas.profile import ProfileUpdate
from app.services.progress import progress_service
from app.services.rating import rating_service


class ProfileService:
    async def update_profile(self, db: AsyncSession, user: User, payload: ProfileUpdate) -> User:
        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            return user

        for field_name, field_value in update_data.items():
            setattr(user, field_name, field_value)

        await db.commit()
        await db.refresh(user)
        return user

    async def get_cabinet(self, db: AsyncSession, user: User) -> dict[str, object]:
        summary = await progress_service.get_progress_summary(db, user)
        active_sessions_stmt = select(func.count(UserSession.id)).where(
            UserSession.user_id == user.id,
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > datetime.now(timezone.utc),
        )
        recent_progress_stmt = (
            select(ScenarioProgress)
            .where(ScenarioProgress.user_id == user.id)
            .order_by(desc(ScenarioProgress.updated_at))
            .limit(5)
        )
        recent_events_stmt = (
            select(ReputationLedger)
            .where(ReputationLedger.user_id == user.id)
            .order_by(desc(ReputationLedger.created_at))
            .limit(5)
        )

        active_sessions = int(await db.scalar(active_sessions_stmt) or 0)
        recent_progress = list((await db.scalars(recent_progress_stmt)).all())
        recent_events = list((await db.scalars(recent_events_stmt)).all())

        return {
            "profile": user,
            "stats": summary,
            "active_sessions": active_sessions,
            "current_rank": await rating_service.get_user_rank(db, user),
            "recent_progress": recent_progress,
            "recent_reputation_events": recent_events,
        }

    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> User:
        user = await db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return user


profile_service = ProfileService()
