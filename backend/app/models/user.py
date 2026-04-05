from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Enum as SAEnum, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import League, UserRole
from app.models.base import TimestampMixin, UTCDateTime, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    bio: Mapped[str | None] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(String(512))
    role: Mapped[UserRole] = mapped_column(
        SAEnum(
            UserRole,
            name="user_role",
            native_enum=False,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=UserRole.PLAYER,
        server_default=text("'player'"),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )
    reputation_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
        index=True,
    )
    league: Mapped[League] = mapped_column(
        SAEnum(
            League,
            name="league",
            native_enum=False,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=League.BRONZE,
        server_default=text("'bronze'"),
        index=True,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(UTCDateTime())

    sessions: Mapped[list["UserSession"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    progresses: Mapped[list["ScenarioProgress"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    attempts: Mapped[list["ScenarioAttempt"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    training_attempts: Mapped[list["TrainingAttempt"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    reputation_events: Mapped[list["ReputationLedger"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
