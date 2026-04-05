from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.core.enums import League, UserRole
from app.schemas.common import ORMSchema


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class LoginRequest(BaseModel):
    login: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class UserSnapshot(ORMSchema):
    id: UUID
    email: EmailStr
    username: str
    full_name: str | None = None
    avatar_url: str | None = None
    role: UserRole
    reputation_score: int
    league: League


class SessionRead(ORMSchema):
    id: UUID
    ip_address: str | None = None
    user_agent: str | None = None
    created_at: datetime
    expires_at: datetime
    last_activity_at: datetime
    revoked_at: datetime | None = None
    is_current: bool = False


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int
    user: UserSnapshot
    session: SessionRead


class SessionsResponse(BaseModel):
    items: list[SessionRead]
