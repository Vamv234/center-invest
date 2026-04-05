from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    JSON,
    Boolean,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UTCDateTime, UUIDPrimaryKeyMixin


class ScenarioProgress(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "scenario_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "scenario_key", name="uq_scenario_progress_user_scenario"),
    )

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scenario_key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    scenario_title: Mapped[str] = mapped_column(String(255), nullable=False)
    attempts_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    completions_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    successes_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    failures_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    total_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default=text("0"))
    average_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default=text("0"))
    best_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default=text("0"))
    success_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default=text("0"))
    total_errors: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    last_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default=text("0"))
    last_result_success: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    last_attempt_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    last_completed_at: Mapped[datetime | None] = mapped_column(UTCDateTime())

    user: Mapped["User"] = relationship(back_populates="progresses")
    attempts: Mapped[list["ScenarioAttempt"]] = relationship(back_populates="progress")


class ScenarioAttempt(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "scenario_attempts"

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    progress_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("scenario_progress.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scenario_key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    scenario_title: Mapped[str] = mapped_column(String(255), nullable=False)
    started_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    finished_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    score_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    errors_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    reputation_delta: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    submission_payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    user: Mapped["User"] = relationship(back_populates="attempts")
    progress: Mapped["ScenarioProgress"] = relationship(back_populates="attempts")
    errors: Mapped[list["ScenarioAttemptError"]] = relationship(
        back_populates="attempt",
        cascade="all, delete-orphan",
    )
    reputation_events: Mapped[list["ReputationLedger"]] = relationship(back_populates="attempt")


class ScenarioAttemptError(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "scenario_attempt_errors"

    attempt_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("scenario_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    error_code: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default="medium", server_default=text("'medium'"))
    penalty_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    context: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    attempt: Mapped["ScenarioAttempt"] = relationship(back_populates="errors")
