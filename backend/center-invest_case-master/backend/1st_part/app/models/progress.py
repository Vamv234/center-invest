from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, func

from app.db.base import Base


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    attack_id = Column(Integer, ForeignKey("attacks.id"), nullable=False, index=True)
    choice_id = Column(Integer, ForeignKey("choices.id"), nullable=False, index=True)
    is_correct = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False, index=True)
    success_rate = Column(Integer, nullable=False, default=0)
    mistakes = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reputation = Column(Integer, nullable=False, default=0)
    league = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
