from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ScenarioCard(BaseModel):
    id: str
    title: str
    level: str
    setting: str
    summary: str
    threat_types: list[str]
    steps_count: int
    passing_score: int


class StepOptionOut(BaseModel):
    id: str
    label: str


class StepOut(BaseModel):
    id: str
    title: str
    prompt: str
    has_hint: bool
    options: list[StepOptionOut]


class ScenarioMeta(BaseModel):
    id: str
    title: str
    level: str
    setting: str
    summary: str
    threat_types: list[str]
    passing_score: int


class SubmitAnswerIn(BaseModel):
    option_id: str = Field(min_length=1, max_length=64)


class AttemptStateOut(BaseModel):
    attempt_id: UUID
    user_id: UUID
    scenario: ScenarioMeta
    status: str
    score: int
    hints_used: int
    answered_steps: int
    total_steps: int
    progress_percent: int
    current_step: StepOut | None


class AnswerFeedbackOut(BaseModel):
    step_id: str
    option_id: str
    outcome: str | None = None
    is_safe: bool
    feedback: str
    explanation: str
    hint: str
    tags: list[str]


class AttemptAnswerResultOut(AttemptStateOut):
    answer_feedback: AnswerFeedbackOut


class AttemptEventOut(BaseModel):
    id: int
    attempt_id: UUID
    event_name: str
    payload: dict[str, object]
    created_at: datetime


class HintResultOut(AttemptStateOut):
    hint: str
    hint_penalty: int
