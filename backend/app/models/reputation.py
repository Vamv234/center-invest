from __future__ import annotations

from uuid import UUID

from sqlalchemy import Enum as SAEnum, ForeignKey, Integer, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import ReputationReason
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class ReputationLedger(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "reputation_ledger"

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    attempt_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("scenario_attempts.id", ondelete="SET NULL"),
        index=True,
    )
    scenario_key: Mapped[str | None] = mapped_column(String(128), index=True)
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[ReputationReason] = mapped_column(
        SAEnum(
            ReputationReason,
            name="reputation_reason",
            native_enum=False,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    context: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    user: Mapped["User"] = relationship(back_populates="reputation_events")
    attempt: Mapped["ScenarioAttempt | None"] = relationship(back_populates="reputation_events")
