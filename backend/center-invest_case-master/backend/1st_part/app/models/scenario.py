from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func

from app.db.base import Base


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    order_index = Column(Integer, nullable=False, default=0)


class Attack(Base):
    __tablename__ = "attacks"

    id = Column(Integer, primary_key=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False, index=True)
    attack_type = Column(String(64), nullable=False)
    description = Column(String(1000), nullable=True)


class Choice(Base):
    __tablename__ = "choices"

    id = Column(Integer, primary_key=True)
    attack_id = Column(Integer, ForeignKey("attacks.id"), nullable=False, index=True)
    label = Column(String(255), nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    hint = Column(String(1000), nullable=True)
    explanation = Column(String(1000), nullable=True)
