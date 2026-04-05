from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AccessContext, get_access_context
from app.core.database import get_db_session
from app.core.redis import get_redis
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    SessionRead,
    SessionsResponse,
    TokenPairResponse,
    UserSnapshot,
    RegisterRequest,
)
from app.schemas.common import MessageResponse
from app.services.auth import auth_service

router = APIRouter()


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _build_token_response(result, current_session_id: UUID | None = None) -> TokenPairResponse:
    session_payload = SessionRead.model_validate(result.session)
    if current_session_id and current_session_id == result.session.id:
        session_payload = session_payload.model_copy(update={"is_current": True})
    return TokenPairResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        expires_in=result.expires_in,
        refresh_expires_in=result.refresh_expires_in,
        user=UserSnapshot.model_validate(result.user),
        session=session_payload,
    )


@router.post("/register", response_model=TokenPairResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> TokenPairResponse:
    result = await auth_service.register(
        db,
        redis,
        payload,
        user_agent=request.headers.get("user-agent"),
        ip_address=_client_ip(request),
    )
    return _build_token_response(result, result.session.id)


@router.post("/login", response_model=TokenPairResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> TokenPairResponse:
    result = await auth_service.login(
        db,
        redis,
        payload,
        user_agent=request.headers.get("user-agent"),
        ip_address=_client_ip(request),
    )
    return _build_token_response(result, result.session.id)


@router.post("/refresh", response_model=TokenPairResponse)
async def refresh(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> TokenPairResponse:
    result = await auth_service.refresh(db, redis, payload.refresh_token)
    return _build_token_response(result, result.session.id)


@router.get("/sessions", response_model=SessionsResponse)
async def list_sessions(
    context: AccessContext = Depends(get_access_context),
    db: AsyncSession = Depends(get_db_session),
) -> SessionsResponse:
    sessions = await auth_service.list_sessions(db, context.user)
    items = [
        SessionRead.model_validate(session).model_copy(update={"is_current": session.id == context.session.id})
        for session in sessions
    ]
    return SessionsResponse(items=items)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    context: AccessContext = Depends(get_access_context),
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> MessageResponse:
    await auth_service.revoke_current_session(db, redis, context.session)
    return MessageResponse(message="Current session revoked.")


@router.delete("/sessions/{session_id}", response_model=MessageResponse)
async def revoke_session(
    session_id: UUID,
    context: AccessContext = Depends(get_access_context),
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> MessageResponse:
    await auth_service.revoke_session(db, redis, user=context.user, session_id=session_id)
    return MessageResponse(message="Session revoked.")
