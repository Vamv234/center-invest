from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.enums import League
from app.schemas.common import ORMSchema


class AttemptErrorInput(BaseModel):
    error_code: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=4000)
    severity: str = Field(default="medium", max_length=32)
    penalty_points: int = Field(default=0, ge=0, le=100)
    context: dict[str, object] = Field(default_factory=dict)


class ScenarioAttemptCreate(BaseModel):
    scenario_key: str = Field(min_length=1, max_length=128)
    scenario_title: str = Field(min_length=1, max_length=255)
    started_at: datetime | None = None
    finished_at: datetime | None = None
    success: bool
    completed: bool | None = None
    score_percentage: float = Field(ge=0, le=100)
    submission_payload: dict[str, object] = Field(default_factory=dict)
    errors: list[AttemptErrorInput] = Field(default_factory=list)


class AttemptErrorRead(ORMSchema):
    id: UUID
    error_code: str
    message: str
    severity: str
    penalty_points: int
    context: dict[str, object]
    created_at: datetime


class ScenarioAttemptRead(ORMSchema):
    id: UUID
    scenario_key: str
    scenario_title: str
    started_at: datetime
    finished_at: datetime
    duration_seconds: int | None = None
    success: bool
    completed: bool
    score_percentage: float
    errors_count: int
    reputation_delta: int
    submission_payload: dict[str, object]
    created_at: datetime
    errors: list[AttemptErrorRead]


class ScenarioProgressRead(ORMSchema):
    id: UUID
    scenario_key: str
    scenario_title: str
    attempts_count: int
    completions_count: int
    successes_count: int
    failures_count: int
    average_score: float
    best_score: float
    success_rate: float
    total_errors: int
    last_score: float
    last_result_success: bool
    last_attempt_at: datetime | None = None
    last_completed_at: datetime | None = None
    updated_at: datetime


class ScenarioProgressDetail(BaseModel):
    progress: ScenarioProgressRead
    recent_attempts: list[ScenarioAttemptRead]


class ProgressSummaryResponse(BaseModel):
    total_scenarios: int
    completed_scenarios: int
    total_attempts: int
    average_success_rate: float
    average_score: float
    total_errors: int
    reputation_score: int
    league: League


class ProgressSubmissionResponse(BaseModel):
    progress: ScenarioProgressRead
    attempt: ScenarioAttemptRead
    summary: ProgressSummaryResponse
    reputation_delta: int
