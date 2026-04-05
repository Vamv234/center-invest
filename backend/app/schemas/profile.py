from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.core.enums import League, ReputationReason, UserRole
from app.schemas.common import ORMSchema


class ProfileRead(ORMSchema):
    id: UUID
    email: EmailStr
    username: str
    full_name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    role: UserRole
    is_active: bool
    reputation_score: int
    league: League
    created_at: datetime
    last_login_at: datetime | None = None


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=2000)
    avatar_url: str | None = Field(default=None, max_length=512)


class CabinetStats(BaseModel):
    total_scenarios: int
    completed_scenarios: int
    total_attempts: int
    average_success_rate: float
    average_score: float
    total_errors: int


class CabinetScenarioSummary(ORMSchema):
    scenario_key: str
    scenario_title: str
    attempts_count: int
    completions_count: int
    best_score: float
    success_rate: float
    last_attempt_at: datetime | None = None


class CabinetReputationEvent(ORMSchema):
    id: UUID
    delta: int
    balance_after: int
    reason: ReputationReason
    description: str
    created_at: datetime
    scenario_key: str | None = None


class CabinetResponse(BaseModel):
    profile: ProfileRead
    stats: CabinetStats
    active_sessions: int
    current_rank: int
    recent_progress: list[CabinetScenarioSummary]
    recent_reputation_events: list[CabinetReputationEvent]
