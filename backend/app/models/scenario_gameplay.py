from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UTCDateTime


class TrainingScenario(Base):
    __tablename__ = "training_scenarios"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[str] = mapped_column(String(32), nullable=False)
    setting: Mapped[str] = mapped_column(String(64), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    threat_types: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    start_step_id: Mapped[str] = mapped_column(String(64), nullable=False)
    passing_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        nullable=False,
        server_default=func.now(),
    )

    steps: Mapped[list["TrainingScenarioStep"]] = relationship(
        back_populates="scenario",
        cascade="all, delete-orphan",
        order_by="TrainingScenarioStep.order_index",
    )
    attempts: Mapped[list["TrainingAttempt"]] = relationship(back_populates="scenario")


class TrainingScenarioStep(Base):
    __tablename__ = "training_scenario_steps"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    scenario_id: Mapped[str] = mapped_column(
        ForeignKey("training_scenarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    hint: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    scenario: Mapped["TrainingScenario"] = relationship(back_populates="steps")
    options: Mapped[list["TrainingStepOption"]] = relationship(
        back_populates="step",
        cascade="all, delete-orphan",
        order_by="TrainingStepOption.order_index",
    )


class TrainingStepOption(Base):
    __tablename__ = "training_step_options"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    step_id: Mapped[str] = mapped_column(
        ForeignKey("training_scenario_steps.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    outcome: Mapped[str | None] = mapped_column(String(32))
    is_safe: Mapped[bool] = mapped_column(Boolean, nullable=False)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    score_delta: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    next_step_id: Mapped[str | None] = mapped_column(String(64))
    ends_attempt: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    step: Mapped["TrainingScenarioStep"] = relationship(back_populates="options")


class TrainingAttempt(Base, TimestampMixin):
    __tablename__ = "training_attempts"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scenario_id: Mapped[str] = mapped_column(
        ForeignKey("training_scenarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    current_step_id: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    hints_used: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )
    progress_synced: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    user: Mapped["User"] = relationship(back_populates="training_attempts")
    scenario: Mapped["TrainingScenario"] = relationship(back_populates="attempts")
    answers: Mapped[list["TrainingAttemptAnswer"]] = relationship(
        back_populates="attempt",
        cascade="all, delete-orphan",
        order_by="TrainingAttemptAnswer.answered_at",
    )
    events: Mapped[list["TrainingEventLog"]] = relationship(
        back_populates="attempt",
        cascade="all, delete-orphan",
        order_by="TrainingEventLog.created_at",
    )


class TrainingAttemptAnswer(Base):
    __tablename__ = "training_attempt_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    attempt_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("training_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_id: Mapped[str] = mapped_column(String(64), nullable=False)
    option_id: Mapped[str] = mapped_column(String(64), nullable=False)
    is_safe: Mapped[bool] = mapped_column(Boolean, nullable=False)
    score_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    answered_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        nullable=False,
        server_default=func.now(),
    )

    attempt: Mapped["TrainingAttempt"] = relationship(back_populates="answers")


class TrainingEventLog(Base):
    __tablename__ = "training_event_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    attempt_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("training_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_id: Mapped[str | None] = mapped_column(String(64), index=True)
    event_name: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        nullable=False,
        server_default=func.now(),
    )

    attempt: Mapped["TrainingAttempt"] = relationship(back_populates="events")
