from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.enums import League, ReputationReason
from app.schemas.common import ORMSchema


class ReputationEventRead(ORMSchema):
    id: UUID
    delta: int
    balance_after: int
    reason: ReputationReason
    description: str
    scenario_key: str | None = None
    created_at: datetime


class RatingOverviewResponse(BaseModel):
    user_id: UUID
    reputation_score: int
    league: League
    rank: int
    next_league: League | None = None
    points_to_next_league: int | None = None
    recent_events: list[ReputationEventRead]


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: UUID
    username: str
    full_name: str | None = None
    avatar_url: str | None = None
    reputation_score: int
    league: League


class LeaderboardResponse(BaseModel):
    items: list[LeaderboardEntry]
    total: int
    limit: int
    offset: int
