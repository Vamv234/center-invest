from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    TokenValidationError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    refresh_token_key,
    verify_password,
)
from app.models.session import UserSession
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.reputation import reputation_service


@dataclass(slots=True)
class AuthResult:
    user: User
    session: UserSession
    access_token: str
    refresh_token: str
    expires_in: int
    refresh_expires_in: int


class AuthService:
    async def register(
        self,
        db: AsyncSession,
        redis: Redis,
        payload: RegisterRequest,
        *,
        user_agent: str | None,
        ip_address: str | None,
    ) -> AuthResult:
        existing_user = await db.scalar(
            select(User).where(
                or_(User.email == payload.email.lower(), User.username == payload.username.lower())
            )
        )
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with the same email or username already exists.",
            )

        user = User(
            email=payload.email.lower(),
            username=payload.username.lower(),
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
        )
        db.add(user)
        await db.flush()
        await reputation_service.award_registration_bonus(db, user)

        result = await self._issue_session(
            db,
            redis,
            user=user,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        await db.commit()
        await db.refresh(user)
        await db.refresh(result.session)
        return result

    async def login(
        self,
        db: AsyncSession,
        redis: Redis,
        payload: LoginRequest,
        *,
        user_agent: str | None,
        ip_address: str | None,
    ) -> AuthResult:
        login_value = payload.login.lower()
        user = await db.scalar(
            select(User).where(or_(User.email == login_value, User.username == login_value))
        )
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials.",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled.",
            )

        user.last_login_at = datetime.now(timezone.utc)
        result = await self._issue_session(
            db,
            redis,
            user=user,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        await db.commit()
        await db.refresh(user)
        await db.refresh(result.session)
        return result

    async def refresh(
        self,
        db: AsyncSession,
        redis: Redis,
        refresh_token: str,
    ) -> AuthResult:
        try:
            payload = decode_token(refresh_token)
        except TokenValidationError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(error),
            ) from error

        if payload.token_type.value != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Wrong token type.",
            )

        session = await db.scalar(
            select(UserSession)
            .where(
                UserSession.id == payload.session_id,
                UserSession.user_id == payload.subject,
            )
        )
        if (
            session is None
            or session.revoked_at is not None
            or session.expires_at <= datetime.now(timezone.utc)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session is no longer active.",
            )

        if session.refresh_token_jti != payload.jti:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been rotated.",
            )

        await self._ensure_refresh_token_is_active(redis, payload.jti, session.id)

        user = await db.get(User, payload.subject)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        old_jti = session.refresh_token_jti
        new_jti = str(uuid4())
        session.refresh_token_jti = new_jti
        session.last_activity_at = datetime.now(timezone.utc)
        session.expires_at = datetime.now(timezone.utc) + settings.refresh_token_ttl

        access_token = create_access_token(user.id, session.id)
        new_refresh_token, _ = create_refresh_token(user.id, session.id, jti=new_jti)
        await self._delete_refresh_token(redis, old_jti)
        await self._store_refresh_token(redis, new_jti, session.id)

        await db.commit()
        await db.refresh(user)
        await db.refresh(session)
        return AuthResult(
            user=user,
            session=session,
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=int(settings.access_token_ttl.total_seconds()),
            refresh_expires_in=int(settings.refresh_token_ttl.total_seconds()),
        )

    async def list_sessions(self, db: AsyncSession, user: User) -> list[UserSession]:
        sessions_stmt = (
            select(UserSession)
            .where(UserSession.user_id == user.id)
            .order_by(UserSession.created_at.desc())
        )
        return list((await db.scalars(sessions_stmt)).all())

    async def revoke_session(
        self,
        db: AsyncSession,
        redis: Redis,
        *,
        user: User,
        session_id: UUID,
    ) -> None:
        session = await db.scalar(
            select(UserSession).where(
                UserSession.id == session_id,
                UserSession.user_id == user.id,
            )
        )
        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

        session.revoked_at = datetime.now(timezone.utc)
        await self._delete_refresh_token(redis, session.refresh_token_jti)
        await db.commit()

    async def revoke_current_session(
        self,
        db: AsyncSession,
        redis: Redis,
        session: UserSession,
    ) -> None:
        session.revoked_at = datetime.now(timezone.utc)
        await self._delete_refresh_token(redis, session.refresh_token_jti)
        await db.commit()

    async def _issue_session(
        self,
        db: AsyncSession,
        redis: Redis,
        *,
        user: User,
        user_agent: str | None,
        ip_address: str | None,
    ) -> AuthResult:
        refresh_jti = str(uuid4())
        now = datetime.now(timezone.utc)
        session = UserSession(
            user_id=user.id,
            refresh_token_jti=refresh_jti,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=now + settings.refresh_token_ttl,
            last_activity_at=now,
        )
        db.add(session)
        await db.flush()

        access_token = create_access_token(user.id, session.id)
        refresh_token, _ = create_refresh_token(user.id, session.id, jti=refresh_jti)
        await self._store_refresh_token(redis, refresh_jti, session.id)

        return AuthResult(
            user=user,
            session=session,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(settings.access_token_ttl.total_seconds()),
            refresh_expires_in=int(settings.refresh_token_ttl.total_seconds()),
        )

    async def _store_refresh_token(self, redis: Redis, jti: str, session_id: UUID) -> None:
        try:
            await redis.setex(
                refresh_token_key(jti),
                int(settings.refresh_token_ttl.total_seconds()),
                str(session_id),
            )
        except RedisError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Redis is unavailable.",
            ) from error

    async def _delete_refresh_token(self, redis: Redis, jti: str) -> None:
        try:
            await redis.delete(refresh_token_key(jti))
        except RedisError:
            return

    async def _ensure_refresh_token_is_active(
        self,
        redis: Redis,
        jti: str,
        session_id: UUID,
    ) -> None:
        try:
            cached_session_id = await redis.get(refresh_token_key(jti))
        except RedisError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Redis is unavailable.",
            ) from error

        if cached_session_id != str(session_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is not active anymore.",
            )


auth_service = AuthService()
