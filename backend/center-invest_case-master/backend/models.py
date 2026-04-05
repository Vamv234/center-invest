"""SQLAlchemy models"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import json

from database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    progress = relationship("UserProgress", back_populates="user")
    certificates = relationship("UserCertificate", back_populates="user")


class AttackScenario(Base):
    __tablename__ = "attack_scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    context = Column(String)  # "office", "home", "public_wifi"
    attack_type = Column(String)  # "phishing", "skimming", "brute_force", "social_engineering", "deepfake"
    difficulty = Column(String)  # "beginner", "intermediate", "advanced"
    attack_steps = Column(JSON)  # Store the scenario steps and choices as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    progress = relationship("UserProgress", back_populates="scenario")
    certificates = relationship("UserCertificate", back_populates="scenario")


class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    scenario_id = Column(Integer, ForeignKey("attack_scenarios.id"))
    status = Column(String, default="in_progress")  # "in_progress", "completed", "failed"
    security_level = Column(Integer, default=100)  # 0-100 HP
    correct_choices = Column(Integer, default=0)
    total_choices = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    scenario = relationship("AttackScenario", back_populates="progress")


class UserCertificate(Base):
    __tablename__ = "user_certificates"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    scenario_id = Column(Integer, ForeignKey("attack_scenarios.id"))
    achievement = Column(String)  # "perfect_score", "first_completion", etc.
    qr_code = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="certificates")
    scenario = relationship("AttackScenario", back_populates="certificates")
