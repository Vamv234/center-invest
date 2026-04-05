from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db_session
from app.core.enums import TokenType
from app.core.security import TokenValidationError, decode_token
from app.models.session import UserSession
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")


@dataclass(slots=True)
class AccessContext:
    user: User
    session: UserSession


async def resolve_access_context(token: str, db: AsyncSession) -> AccessContext:
    try:
        payload = decode_token(token)
    except TokenValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error

    if payload.token_type is not TokenType.ACCESS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required.",
        )

    session = await db.get(UserSession, payload.session_id)
    if session is None or session.user_id != payload.subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found.",
        )
    if session.revoked_at is not None or session.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is no longer active.",
        )

    user = await db.get(User, payload.subject)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not available.",
        )

    return AccessContext(user=user, session=session)


async def get_access_context(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> AccessContext:
    return await resolve_access_context(token, db)
